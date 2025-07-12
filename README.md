# Anniversary Holiday Coverage Optimizer (Türkiye 2025-2074)

Evlilik yıldönümü için optimal tarih önerisi sistemi. 2025-2074 yılları arasında, seçilen tarihin her yıl mümkün olduğunca resmî/dinî tatil + köprü + hafta sonu bloğunun içinde olmasını sağlayan en iyi tarihleri bulur.

## 🎯 Amaç

Bu proje, evlilik yıldönümü için seçilecek tarihin 50 yıllık süreçte en fazla uzun tatil imkanı sağlamasını hedefler. Sistem:

- **Extended Holiday Block** içinde olan yılları 4 puan
- **1 gün mesafede** (Pazartesi/Cuma) olan yılları 2 puan  
- **2 gün mesafede** (Salı/Perşembe) olan yılları 1 puan
- Diğer durumları 0 puan olarak değerlendirir

## 📊 Özellikler

- ✅ **Kapsamlı Analiz**: 365 gün/ay kombinasyonu (Şubat 29 hariç)
- ✅ **Gerçek Tatil Verileri**: Türkiye'nin resmî tatilleri + dinî bayramlar
- ✅ **Hijri Takvim Desteği**: Ramazan ve Kurban bayramları için doğru hesaplama
- ✅ **Köprü Tatili Stratejisi**: Salı başlayan tatiller için Pazartesi, Perşembe biten için Cuma köprüsü
- ✅ **Görselleştirme**: Isı haritası ile aylık performans analizi
- ✅ **Detaylı Raporlama**: Markdown formatında kapsamlı analiz raporu

## 🚀 Kurulum

### Gereksinimler

```bash
pip install -r requirements.txt
```

### Gerekli Kütüphaneler

- `pandas` >= 1.5.0
- `numpy` >= 1.21.0  
- `holidays` >= 0.29
- `hijri-converter` >= 2.3.0
- `plotly` >= 5.0.0
- `matplotlib` >= 3.5.0
- `seaborn` >= 0.11.0

## 📖 Kullanım

### Temel Kullanım

```python
from anniversary_optimizer import AnniversaryOptimizer

# Optimizer'ı başlat
optimizer = AnniversaryOptimizer(
    years_range=(2025, 2075),  # Analiz yılları
    weights=(4, 2, 1, 0),      # Puan ağırlıkları
    bridge_policy="public_sector",  # Köprü politikası
    include_feb29=False        # Şubat 29 dahil etme
)

# Analiz yap
candidates = optimizer.optimize()

# Rapor oluştur
report, top_10 = optimizer.generate_report(candidates)

# Görselleştirme
optimizer.generate_visualization(candidates)
```

### Komut Satırından Çalıştırma

```bash
python anniversary_optimizer.py
```

## 📁 Çıktı Dosyaları

Program çalıştırıldığında aşağıdaki dosyalar oluşturulur:

1. **`anniversary_scores.csv`** - Tüm tarihlerin skorları
2. **`anniversary_report.md`** - Kapsamlı analiz raporu
3. **`anniversary_heatmap.html`** - Isı haritası görselleştirmesi

## 🏆 Sonuç Formatı

### CSV Çıktısı
```csv
day,month,date_str,month_name,anniversary_score,years_in_block,avg_block_length,coverage_percent,efficiency_ratio
1,1,01/01,January,200,50,20.8,100.0,100.0
23,4,23/04,April,200,50,20.8,100.0,100.0
1,5,01/05,May,200,50,20.8,100.0,100.0
...
```

### Rapor İçeriği
- 🏆 En iyi 10 tarih sıralaması
- 📊 Aylık performans analizi
- 🌍 Mevsimsel değerlendirme
- 🎯 Özel tavsiyeler (yaz/kış seçenekleri)
- ⚠️ Önemli notlar ve uyarılar

## ⚙️ Parametreler

### AnniversaryOptimizer Parametreleri

| Parametre | Varsayılan | Açıklama |
|-----------|------------|----------|
| `years_range` | (2025, 2075) | Analiz edilecek yıl aralığı |
| `weights` | (4, 2, 1, 0) | Puan ağırlıkları (block içi, ±1 gün, ±2 gün, diğer) |
| `bridge_policy` | "public_sector" | Köprü tatili politikası |
| `include_feb29` | False | Şubat 29'u dahil etme |

### Köprü Politikaları

- **"public_sector"**: Salı başlayan tatiller için Pazartesi, Perşembe biten için Cuma köprüsü
- **"strict"**: Sadece resmî tatil günleri

## 📈 Metodoloji

### 1. Tatil Verileri
- **Sabit Tatiller**: Türkiye'nin resmî tatilleri (1 Ocak, 23 Nisan, vb.)
- **Dinî Bayramlar**: Ramazan (3 gün) ve Kurban (4 gün) bayramları
- **Hijri Hesaplama**: `hijri-converter` kütüphanesi ile doğru tarih hesaplama

### 2. Extended Block Oluşturma
- Tatil bloklarını birleştirme (2 gün arayla)
- Hafta sonu ekleme (öncesi ve sonrası)
- Köprü günleri ekleme (politikaya göre)

### 3. Skor Hesaplama
- **Block içinde**: 4 puan
- **1 gün mesafede** (Pzt/Cum): 2 puan
- **2 gün mesafede** (Sal/Per): 1 puan
- **Diğer**: 0 puan

## 🎯 Seçenek Kategorileri

### 🏆 "Kolay Seçenekler" (Resmî Tatiller)
Bu tarihler her yıl kesinlikle tatil bloğu içinde yer alır:
- **01/01 (Ocak)** - 200 puan - %100 kapsam
- **23/04 (Nisan)** - 200 puan - %100 kapsam  
- **01/05 (Mayıs)** - 200 puan - %100 kapsam
- **19/05 (Mayıs)** - 200 puan - %100 kapsam
- **15/07 (Temmuz)** - 200 puan - %100 kapsam
- **30/08 (Ağustos)** - 200 puan - %100 kapsam
- **29/10 (Ekim)** - 200 puan - %100 kapsam

### 🧠 "Akıllı Seçenekler" (Dinî Bayram & Köprü Tatili)
Dinî bayramlara yakın veya köprü tatili avantajı olan tarihler:
- **14/07 (Temmuz)** - 82 puan - %34 kapsam - Ramazan Bayramı yakını
- **30/04 (Nisan)** - 76 puan - %32 kapsam - 23 Nisan'a yakın
- **02/01 (Ocak)** - 74 puan - %30 kapsam - Yılbaşına yakın
- **02/05 (Mayıs)** - 74 puan - %30 kapsam - 1 Mayıs'a yakın
- **31/08 (Ağustos)** - 74 puan - %30 kapsam - 30 Ağustos'a yakın
- **20/05 (Mayıs)** - 72 puan - %30 kapsam - 19 Mayıs'a yakın
- **16/07 (Temmuz)** - 72 puan - %28 kapsam - 15 Temmuz'a yakın

### 🌟 "Yaratıcı Seçenekler" (Beklenmedik Avantajlar)
Sürpriz şekilde yüksek skor alan tarihler:
- **01/09 (Eylül)** - 64 puan - %18 kapsam - Okul açılışı dönemi
- **17/07 (Temmuz)** - 61 puan - %16 kapsam - Yaz ortası
- **31/10 (Ekim)** - 61 puan - %16 kapsam - 29 Ekim'e yakın
- **03/01 (Ocak)** - 60 puan - %16 kapsam - Yılbaşı sonrası
- **29/04 (Nisan)** - 60 puan - %16 kapsam - 23 Nisan sonrası
- **03/05 (Mayıs)** - 59 puan - %16 kapsam - 1 Mayıs sonrası
- **21/05 (Mayıs)** - 59 puan - %16 kapsam - 19 Mayıs sonrası

### 🌍 Mevsimsel Analiz
- **İlkbahar**: En yüksek ortalama skor (20.2 puan)
- **Sonbahar**: Orta seviye performans (14.7 puan)
- **Yaz**: Orta seviye performans (14.1 puan)
- **Kış**: Düşük performans (8.4 puan)

## 🔧 Geliştirme

### Yeni Özellik Ekleme

1. **Maliyet Skoru**: Turizm maliyetlerini dahil etme
2. **Mevsim Skoru**: Hava durumu verilerini entegrasyon
3. **Dinî Sapma Toleransı**: ±1 gün kayma için ceza sistemi
4. **Çift Özel Günleri**: Doğum günleriyle çakışma analizi

### Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 🤝 İletişim

Sorularınız veya önerileriniz için:
- GitHub Issues: [Proje sayfası](https://github.com/batuhancetinkaya1/Best-Wedding-Date)
- Email: [batuhan1ec@gmail.com]

## 🙏 Teşekkürler

- `holidays` kütüphanesi için
- `hijri-converter` kütüphanesi için
- Türkiye tatil takvimi verileri için

---

*"Aşkın en güzel günü, her yıl en uzun tatille kutlansın!" 💕*

