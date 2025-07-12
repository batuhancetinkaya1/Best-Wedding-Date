#!/usr/bin/env python3
"""
Anniversary Holiday Coverage Optimizer (Türkiye 2025-2074)
Evlilik yıldönümü için optimal tarih önerisi sistemi
"""

import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import holidays
from hijri_converter import Gregorian, Hijri
import calendar
import warnings
from collections import defaultdict
import json
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
warnings.filterwarnings('ignore')

class TurkeyHolidayManager:
    """Türkiye tatil yöneticisi - Sabit ve dinî tatilleri yönetir"""
    
    def __init__(self):
        self.fixed_holidays = {
            'Yılbaşı': (1, 1),
            'Ulusal Egemenlik ve Çocuk Bayramı': (4, 23),
            'Emek ve Dayanışma Günü': (5, 1),
            'Atatürk\'ü Anma Gençlik ve Spor Bayramı': (5, 19),
            'Demokrasi ve Millî Birlik Günü': (7, 15),
            'Zafer Bayramı': (8, 30),
            'Cumhuriyet Bayramı': (10, 29)
        }
        
    def get_fixed_holidays(self, year):
        """Sabit tatilleri al"""
        holidays_set = set()
        for name, (month, day) in self.fixed_holidays.items():
            try:
                holidays_set.add(date(year, month, day))
            except ValueError:
                continue
        return holidays_set
    
    def get_religious_holidays(self, year):
        """Dinî bayramları hesapla (hijri-converter kullanarak)"""
        religious_holidays = set()
        
        try:
            # Ramazan Bayramı (1 Şevval, 3 gün)
            # Hijri yılı yaklaşık hesapla
            hijri_year = int((year - 622) * 365.25 / 354.37) + 1
            
            # 1 Şevval'i bul
            for day in range(1, 31):
                try:
                    hijri_date = Hijri(hijri_year, 10, day)
                    gregorian_date = hijri_date.to_gregorian()
                    
                    if gregorian_date.year == year:
                        # 3 günlük bayram
                        for i in range(3):
                            bayram_date = gregorian_date + timedelta(days=i)
                            if bayram_date.year == year:
                                religious_holidays.add(bayram_date)
                        break
                except:
                    continue
            
            # Kurban Bayramı (10 Zilhicce, 4 gün)
            for day in range(1, 31):
                try:
                    hijri_date = Hijri(hijri_year, 12, day)
                    gregorian_date = hijri_date.to_gregorian()
                    
                    if gregorian_date.year == year:
                        # 4 günlük bayram
                        for i in range(4):
                            bayram_date = gregorian_date + timedelta(days=i)
                            if bayram_date.year == year:
                                religious_holidays.add(bayram_date)
                        break
                except:
                    continue
                    
        except Exception as e:
            print(f"Dinî bayram hesaplama hatası ({year}): {e}")
            # Fallback: yaklaşık hesaplama
            religious_holidays = self._fallback_religious_holidays(year)
            
        return religious_holidays
    
    def _fallback_religious_holidays(self, year):
        """Fallback dinî bayram hesaplama"""
        religious_holidays = set()
        
        # Basit yaklaşım: her yıl 11 gün öne kayar
        base_year = 2025
        year_diff = year - base_year
        
        # Ramazan Bayramı (yaklaşık)
        base_ramazan = date(2025, 3, 31)
        ramazan_shift = (year_diff * 11) % 365
        try:
            ramazan_date = base_ramazan - timedelta(days=ramazan_shift)
            if ramazan_date.year == year:
                for i in range(3):
                    religious_holidays.add(ramazan_date + timedelta(days=i))
        except:
            pass
            
        # Kurban Bayramı (Ramazan'dan 70 gün sonra)
        try:
            kurban_date = ramazan_date + timedelta(days=70)
            if kurban_date.year == year:
                for i in range(4):
                    religious_holidays.add(kurban_date + timedelta(days=i))
        except:
            pass
            
        return religious_holidays

class HolidayBlockAnalyzer:
    """Tatil bloklarını analiz eden sınıf"""
    
    def __init__(self, bridge_policy="public_sector"):
        self.bridge_policy = bridge_policy
        
    def create_holiday_blocks(self, holidays_set):
        """Tatil bloklarını oluştur"""
        if not holidays_set:
            return []
            
        sorted_holidays = sorted(holidays_set)
        blocks = []
        current_block = []
        
        for holiday in sorted_holidays:
            if not current_block:
                current_block = [holiday]
            else:
                # İki gün arayla veya bitişik ise aynı bloğa ekle
                if (holiday - current_block[-1]).days <= 2:
                    current_block.append(holiday)
                else:
                    blocks.append(current_block)
                    current_block = [holiday]
        
        if current_block:
            blocks.append(current_block)
            
        return blocks
    
    def extend_block(self, block):
        """Holiday block'u extended block'a çevir"""
        if not block:
            return set()
            
        start_date = min(block)
        end_date = max(block)
        
        extended = set(block)
        
        # Önceki hafta sonu ekle (maksimum 7 gün geriye)
        current = start_date - timedelta(days=1)
        days_back = 0
        while current.weekday() != 6 and days_back < 7:
            if current.weekday() in [5, 6]:  # Cumartesi, Pazar
                extended.add(current)
            current -= timedelta(days=1)
            days_back += 1
        
        # Sonraki hafta sonu ekle (maksimum 7 gün ileriye)
        current = end_date + timedelta(days=1)
        days_forward = 0
        while current.weekday() != 6 and days_forward < 7:
            if current.weekday() in [5, 6]:  # Cumartesi, Pazar
                extended.add(current)
            current += timedelta(days=1)
            days_forward += 1
        
        # Köprü günleri ekle
        if self.bridge_policy == "public_sector":
            # Salı başlarsa Pazartesi köprüsü
            if start_date.weekday() == 1:  # Salı
                monday = start_date - timedelta(days=1)
                extended.add(monday)
                
            # Perşembe biterse Cuma köprüsü
            if end_date.weekday() == 3:  # Perşembe
                friday = end_date + timedelta(days=1)
                extended.add(friday)
        
        return extended

class AnniversaryOptimizer:
    """Ana Anniversary Optimizer sınıfı"""
    
    def __init__(self, years_range=(2025, 2075), weights=(4, 2, 1, 0), 
                 bridge_policy="public_sector", include_feb29=False):
        self.years = list(range(years_range[0], years_range[1]))
        self.weights = weights  # in-block, ±1, ±2, diğer
        self.bridge_policy = bridge_policy
        self.include_feb29 = include_feb29
        
        self.holiday_manager = TurkeyHolidayManager()
        self.block_analyzer = HolidayBlockAnalyzer(bridge_policy)
        
        # Cache için
        self._holiday_cache = {}
        self._extended_blocks_cache = {}
        
    def get_all_holidays(self, year):
        """Bir yılın tüm tatillerini al (cache'li)"""
        if year in self._holiday_cache:
            return self._holiday_cache[year]
            
        fixed_holidays = self.holiday_manager.get_fixed_holidays(year)
        religious_holidays = self.holiday_manager.get_religious_holidays(year)
        
        all_holidays = fixed_holidays.union(religious_holidays)
        self._holiday_cache[year] = all_holidays
        
        return all_holidays
    
    def get_extended_blocks(self, year):
        """Bir yılın extended block'larını al (cache'li)"""
        if year in self._extended_blocks_cache:
            return self._extended_blocks_cache[year]
            
        holidays = self.get_all_holidays(year)
        blocks = self.block_analyzer.create_holiday_blocks(holidays)
        
        extended_blocks = []
        for block in blocks:
            extended = self.block_analyzer.extend_block(block)
            extended_blocks.append(extended)
            
        self._extended_blocks_cache[year] = extended_blocks
        return extended_blocks
    
    def calculate_anniversary_score(self, day, month):
        """Belirli bir gün/ay için Anniversary Score hesapla"""
        total_score = 0
        years_in_block = 0
        block_lengths = []
        score_details = {
            'in_block': 0,
            'one_day_away': 0,
            'two_days_away': 0,
            'other': 0
        }
        
        for year in self.years:
            try:
                target_date = date(year, month, day)
            except ValueError:
                # Şubat 29 gibi geçersiz tarihler için
                continue
                
            # O yılın extended block'larını al
            extended_blocks = self.get_extended_blocks(year)
            
            # Tüm extended block günlerini birleştir
            all_extended_days = set()
            for block in extended_blocks:
                all_extended_days.update(block)
                
            # Mesafeyi hesapla
            if target_date in all_extended_days:
                total_score += self.weights[0]
                years_in_block += 1
                block_lengths.append(len(all_extended_days))
                score_details['in_block'] += 1
            else:
                # En yakın extended block gününe mesafe
                if all_extended_days:
                    min_distance = min(abs((target_date - eb_day).days) 
                                     for eb_day in all_extended_days)
                    
                    if min_distance == 1 and target_date.weekday() in [0, 4]:  # Pzt, Cum
                        total_score += self.weights[1]
                        score_details['one_day_away'] += 1
                    elif min_distance == 2 and target_date.weekday() in [1, 3]:  # Sal, Per
                        total_score += self.weights[2]
                        score_details['two_days_away'] += 1
                    else:
                        score_details['other'] += 1
                else:
                    score_details['other'] += 1
                        
        avg_block_length = np.mean(block_lengths) if block_lengths else 0
        
        return {
            'score': total_score,
            'years_in_block': years_in_block,
            'avg_block_length': avg_block_length,
            'score_details': score_details,
            'max_possible_score': len(self.years) * self.weights[0]
        }
    
    def optimize(self):
        """Tüm tarih kombinasyonlarını değerlendir"""
        candidates = []
        
        print("Tüm tarih kombinasyonları analiz ediliyor...")
        
        # Tüm gün/ay kombinasyonlarını test et
        for month in range(1, 13):
            print(f"  {calendar.month_name[month]} ayı işleniyor...")
            
            # O ayın maksimum gün sayısını al
            max_days = calendar.monthrange(2025, month)[1]
            
            for day in range(1, max_days + 1):
                # Şubat 29 kontrolü
                if month == 2 and day == 29 and not self.include_feb29:
                    continue
                
                try:
                    # Geçerli tarih kontrolü
                    date(2025, month, day)
                    
                    result = self.calculate_anniversary_score(day, month)
                    
                    candidates.append({
                        'day': day,
                        'month': month,
                        'date_str': f"{day:02d}/{month:02d}",
                        'month_name': calendar.month_name[month],
                        'anniversary_score': result['score'],
                        'years_in_block': result['years_in_block'],
                        'avg_block_length': result['avg_block_length'],
                        'coverage_percent': (result['years_in_block'] / len(self.years)) * 100,
                        'efficiency_ratio': (result['score'] / result['max_possible_score']) * 100,
                        'score_details': result['score_details']
                    })
                    
                except ValueError:
                    # Geçersiz tarih (örn: 31 Şubat)
                    continue
        
        # Skorlara göre sırala
        candidates.sort(key=lambda x: x['anniversary_score'], reverse=True)
        
        return candidates
    
    def generate_visualization(self, candidates, filename='anniversary_heatmap.html'):
        """Isı haritası görselleştirmesi oluştur"""
        # Aylık ortalama skorları hesapla
        monthly_scores = defaultdict(list)
        for candidate in candidates:
            monthly_scores[candidate['month']].append(candidate['anniversary_score'])
        
        monthly_avg = {month: np.mean(scores) for month, scores in monthly_scores.items()}
        
        # Isı haritası için veri hazırla
        heatmap_data = []
        for month in range(1, 13):
            month_scores = [c['anniversary_score'] for c in candidates if c['month'] == month]
            if month_scores:
                max_days = max(c['day'] for c in candidates if c['month'] == month)
                for day in range(1, max_days + 1):
                    score = next((c['anniversary_score'] for c in candidates 
                                if c['month'] == month and c['day'] == day), 0)
                    heatmap_data.append([day, month, score])
        
        df_heatmap = pd.DataFrame(heatmap_data, columns=['Day', 'Month', 'Score'])
        pivot_data = df_heatmap.pivot(index='Day', columns='Month', values='Score')
        
        # Plotly ile ısı haritası
        fig = go.Figure(data=go.Heatmap(
            z=pivot_data.values,
            x=[calendar.month_name[i] for i in range(1, 13)],
            y=list(range(1, 32)),
            colorscale='RdYlBu_r',
            hoverongaps=False,
            hovertemplate='Gün: %{y}<br>Ay: %{x}<br>Skor: %{z}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Anniversary Score Isı Haritası (2025-2074)',
            xaxis_title='Ay',
            yaxis_title='Gün',
            height=600
        )
        
        fig.write_html(filename)
        return fig
    
    def generate_report(self, candidates):
        """Kapsamlı rapor oluştur"""
        top_10 = candidates[:10]
        
        # İstatistikler
        total_candidates = len(candidates)
        max_score = candidates[0]['anniversary_score']
        min_score = candidates[-1]['anniversary_score']
        avg_score = np.mean([c['anniversary_score'] for c in candidates])
        
        # Aylık performans
        monthly_stats = defaultdict(list)
        for candidate in candidates:
            monthly_stats[candidate['month']].append(candidate['anniversary_score'])
        
        monthly_avg = {month: np.mean(scores) for month, scores in monthly_stats.items()}
        best_months = sorted(monthly_avg.items(), key=lambda x: x[1], reverse=True)
        
        # Sezon analizi
        seasons = {
            'Kış': [12, 1, 2],
            'İlkbahar': [3, 4, 5],
            'Yaz': [6, 7, 8],
            'Sonbahar': [9, 10, 11]
        }
        
        season_stats = {}
        for season, months in seasons.items():
            season_scores = [c['anniversary_score'] for c in candidates if c['month'] in months]
            season_stats[season] = np.mean(season_scores) if season_scores else 0
        
        # Rapor oluştur
        report = f"""# Anniversary Holiday Coverage Optimizer - Türkiye 2025-2074
## Kapsamlı Analiz Raporu

### 📊 Metodoloji ve Parametreler
- **Analiz Dönemi**: {self.years[0]} - {self.years[-1]} ({len(self.years)} yıl)
- **Toplam Analiz Edilen Tarih**: {total_candidates:,} farklı gün/ay kombinasyonu
- **Köprü Politikası**: {self.bridge_policy}
- **Şubat 29 Dahil**: {'Evet' if self.include_feb29 else 'Hayır'}
- **Değerlendirme Kriterleri**: 
  - Extended Block içinde: {self.weights[0]} puan
  - 1 gün mesafede (Pazartesi/Cuma): {self.weights[1]} puan  
  - 2 gün mesafede (Salı/Perşembe): {self.weights[2]} puan
  - Diğer durumlar: {self.weights[3]} puan
- **Maksimum Olası Skor**: {self.weights[0] * len(self.years)} puan

### 🏆 En İyi 10 Tarih

| Sıra | Tarih | Ay | Anniversary Score | Block İçi Yıl | Kapsam (%) | Verimlilik (%) | Ort. Block Uzunluğu |
|------|-------|-----|------------------|----------------|------------|----------------|---------------------|
"""
        
        for i, candidate in enumerate(top_10, 1):
            report += f"| {i} | {candidate['date_str']} | {candidate['month_name']} | {candidate['anniversary_score']} | {candidate['years_in_block']} | {candidate['coverage_percent']:.1f}% | {candidate['efficiency_ratio']:.1f}% | {candidate['avg_block_length']:.1f} gün |\n"
        
        report += f"""

### 🥇 CHAMPION: {top_10[0]['date_str']} ({top_10[0]['month_name']})
- **🏆 Anniversary Score**: {top_10[0]['anniversary_score']}/{self.weights[0] * len(self.years)} (%{top_10[0]['efficiency_ratio']:.1f} verimlilik)
- **📅 Tatil bloğu içinde**: {top_10[0]['years_in_block']} yıl (50 yılın %{top_10[0]['coverage_percent']:.1f}'i)
- **⏱️ Ortalama tatil uzunluğu**: {top_10[0]['avg_block_length']:.1f} gün
- **📊 Skor Detayları**: 
  - Block içinde: {top_10[0]['score_details']['in_block']} yıl
  - 1 gün mesafede: {top_10[0]['score_details']['one_day_away']} yıl
  - 2 gün mesafede: {top_10[0]['score_details']['two_days_away']} yıl
  - Diğer: {top_10[0]['score_details']['other']} yıl
- **🎯 Tavsiye**: En yüksek skor! 50 yıllık süreçte en fazla uzun tatil garantisi.

### 🥈 RUNNER-UP: {top_10[1]['date_str']} ({top_10[1]['month_name']})
- **🏆 Anniversary Score**: {top_10[1]['anniversary_score']}/{self.weights[0] * len(self.years)} (%{top_10[1]['efficiency_ratio']:.1f} verimlilik)
- **📅 Tatil bloğu içinde**: {top_10[1]['years_in_block']} yıl (50 yılın %{top_10[1]['coverage_percent']:.1f}'i)
- **⏱️ Ortalama tatil uzunluğu**: {top_10[1]['avg_block_length']:.1f} gün
- **🎯 Tavsiye**: Güçlü alternatif seçenek.

### 🥉 THIRD PLACE: {top_10[2]['date_str']} ({top_10[2]['month_name']})
- **🏆 Anniversary Score**: {top_10[2]['anniversary_score']}/{self.weights[0] * len(self.years)} (%{top_10[2]['efficiency_ratio']:.1f} verimlilik)
- **📅 Tatil bloğu içinde**: {top_10[2]['years_in_block']} yıl (50 yılın %{top_10[2]['coverage_percent']:.1f}'i)
- **⏱️ Ortalama tatil uzunluğu**: {top_10[2]['avg_block_length']:.1f} gün
- **🎯 Tavsiye**: Sağlam üçüncü seçenek.

### 📊 Aylık Performans Sıralaması
"""
        
        for i, (month, avg_score) in enumerate(best_months, 1):
            month_name = calendar.month_name[month]
            report += f"{i:2d}. **{month_name}**: {avg_score:.1f} ortalama puan\n"
        
        report += f"""

### 🌍 Mevsimsel Analiz
"""
        
        season_ranking = sorted(season_stats.items(), key=lambda x: x[1], reverse=True)
        for i, (season, avg_score) in enumerate(season_ranking, 1):
            report += f"{i}. **{season}**: {avg_score:.1f} ortalama puan\n"
        
        report += f"""

### 🎯 Özel Durumlar ve Tavsiyeler

#### 🏖️ Yaz Tatili Sevenler İçin
En iyi yaz tarihleri:
"""
        
        summer_dates = [c for c in candidates if c['month'] in [6, 7, 8]][:5]
        for i, candidate in enumerate(summer_dates, 1):
            report += f"- {candidate['date_str']} ({candidate['month_name']}) - {candidate['anniversary_score']} puan\n"
        
        report += f"""

#### 🌸 İlkbahar Önerileri
En iyi ilkbahar tarihleri:
"""
        
        spring_dates = [c for c in candidates if c['month'] in [3, 4, 5]][:5]
        for i, candidate in enumerate(spring_dates, 1):
            report += f"- {candidate['date_str']} ({candidate['month_name']}) - {candidate['anniversary_score']} puan\n"
        
        report += f"""

#### 🍂 Sonbahar Alternatifi
En iyi sonbahar tarihleri:
"""
        
        autumn_dates = [c for c in candidates if c['month'] in [9, 10, 11]][:5]
        for i, candidate in enumerate(autumn_dates, 1):
            report += f"- {candidate['date_str']} ({candidate['month_name']}) - {candidate['anniversary_score']} puan\n"
        
        report += f"""

#### ❄️ Kış Seçenekleri
En iyi kış tarihleri:
"""
        
        winter_dates = [c for c in candidates if c['month'] in [12, 1, 2]][:5]
        for i, candidate in enumerate(winter_dates, 1):
            report += f"- {candidate['date_str']} ({candidate['month_name']}) - {candidate['anniversary_score']} puan\n"
        
        report += f"""

### ⚠️ Önemli Notlar ve Uyarılar

#### 🕌 Dinî Bayramlar
- Ramazan ve Kurban bayramları hijri takvime göre her yıl 11 gün öne kayar
- Hesaplamalarda ±1 gün sapma olabilir
- Dinî bayram dönemlerinde uzun tatil imkanı artar

#### 💰 Maliyet Faktörleri
- Yaz ayları (Haziran-Ağustos) turizm maliyetleri yüksek
- Kurban Bayramı döneminde yurt içi turizm yoğun
- Şubat-Mart arası düşük sezon, daha ekonomik

#### 🏨 Rezervasyon Stratejileri
- Yüksek skorlu tarihlerde erken rezervasyon önemli
- Popüler tatil bölgelerinde alternatif planlar hazırlanmalı
- Köprü tatillerinde trafik yoğunluğu beklenebilir

### 📈 İstatistiksel Özetler

- **En yüksek skor**: {max_score} puan
- **En düşük skor**: {min_score} puan  
- **Ortalama skor**: {avg_score:.1f} puan
- **100+ puan alan tarih sayısı**: {len([c for c in candidates if c['anniversary_score'] >= 100])} adet
- **50+ puan alan tarih sayısı**: {len([c for c in candidates if c['anniversary_score'] >= 50])} adet

### 🎊 Sonuç ve Nihai Tavsiye

**🏆 WINNER: {candidates[0]['date_str']} ({candidates[0]['month_name']})**

Bu tarih, 50 yıllık süreçte en fazla uzun tatil garantisi sunan optimal seçimdir. 
{candidates[0]['years_in_block']} yıl boyunca extended holiday block içinde yer alarak,
ortalama {candidates[0]['avg_block_length']:.1f} günlük tatil imkanı sağlamaktadır.

**Alternatif seçenekler**: {candidates[1]['date_str']} ve {candidates[2]['date_str']} tarihleri de güçlü alternatiflerdir.

*"Aşkın en güzel günü, her yıl en uzun tatille kutlansın!" 💕*

---
*Rapor oluşturma tarihi: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*
"""
        
        return report, top_10

def main():
    """Ana program"""
    print("🚀 Anniversary Holiday Coverage Optimizer başlatılıyor...")
    
    # Optimizer'ı başlat
    optimizer = AnniversaryOptimizer(
        years_range=(2025, 2075), 
        weights=(4, 2, 1, 0),
        bridge_policy="public_sector",
        include_feb29=False
    )
    
    print("Tarih kombinasyonları analiz ediliyor...")
    candidates = optimizer.optimize()
    
    print("Rapor oluşturuluyor...")
    report, top_10 = optimizer.generate_report(candidates)
    
    print("Görselleştirme oluşturuluyor...")
    optimizer.generate_visualization(candidates)
    
    # Sonuçları kaydet
    df = pd.DataFrame(candidates)
    df.to_csv('anniversary_scores.csv', index=False)
    
    with open('anniversary_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\n" + "="*80)
    print("🎉 ANNIVERSARY HOLIDAY COVERAGE OPTIMIZER SONUÇLARI 🎉")
    print("="*80)
    
    print(f"\n📈 Analiz İstatistikleri:")
    print(f"   • Toplam analiz edilen tarih: {len(candidates):,} adet")
    print(f"   • En yüksek skor: {candidates[0]['anniversary_score']} puan")
    print(f"   • Ortalama skor: {np.mean([c['anniversary_score'] for c in candidates]):.1f} puan")
    print(f"   • 100+ puan alan tarih: {len([c for c in candidates if c['anniversary_score'] >= 100])} adet")
    
    print(f"\n🏆 TOP 10 SONUÇLARI:")
    print(f"{'Sıra':<4} {'Tarih':<8} {'Ay':<10} {'Skor':<5} {'Block İçi':<10} {'Kapsam':<8} {'Verimlilik':<10}")
    print("-" * 70)
    
    for i, candidate in enumerate(top_10, 1):
        print(f"{i:<4} {candidate['date_str']:<8} {candidate['month_name'][:9]:<10} {candidate['anniversary_score']:<5} {candidate['years_in_block']:<10} {candidate['coverage_percent']:.1f}%{'':<3} {candidate['efficiency_ratio']:.1f}%")
    
    print(f"\n🥇 CHAMPION: {candidates[0]['date_str']} ({candidates[0]['month_name']})")
    print(f"   🏆 Anniversary Score: {candidates[0]['anniversary_score']}/200 (%{candidates[0]['efficiency_ratio']:.1f} verimlilik)")
    print(f"   📅 Tatil bloğu içinde: {candidates[0]['years_in_block']} yıl (%{candidates[0]['coverage_percent']:.1f} kapsam)")
    print(f"   ⏱️ Ortalama tatil uzunluğu: {candidates[0]['avg_block_length']:.1f} gün")
    
    print(f"\n💡 Hızlı Tavsiyeler:")
    print(f"   • En garantili seçim: {candidates[0]['date_str']} ({candidates[0]['month_name']})")
    print(f"   • Alternatif seçenekler: {candidates[1]['date_str']}, {candidates[2]['date_str']}")
    
    summer_best = [c for c in candidates if c['month'] in [6,7,8]][:3]
    if summer_best:
        print(f"   • Yaz sevenler için: {[c['date_str'] for c in summer_best]}")
    
    winter_best = [c for c in candidates if c['month'] in [2,3,11]][:3]
    if winter_best:
        print(f"   • Ekonomik seçenekler: {[c['date_str'] for c in winter_best]}")
    
    print(f"\n📝 Dosyalar oluşturuldu:")
    print(f"   📊 anniversary_scores.csv")
    print(f"   📋 anniversary_report.md")
    print(f"   📈 anniversary_heatmap.html")
    
    return candidates

if __name__ == "__main__":
    results = main() 