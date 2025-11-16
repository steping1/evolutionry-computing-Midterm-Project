import math
import random # Artık tüm importlar en üstte

# --- 1. ADIM: ZEMİN HAZIRLIĞI ---

class Sehir:
    """
    .tsp dosyasındaki bir şehri (düğümü) temsil eder.
    id, x ve y koordinatlarını tutar.
    """
    def __init__(self, id, x, y):
        self.id = int(id)
        self.x = float(x)
        self.y = float(y)

    def __repr__(self):
        """
        Bir Sehir nesnesini print() ile yazdırırken
        daha okunaklı bir çıktı vermesi için kullanılır.
        """
        return f"Sehir {self.id} ({self.x}, {self.y})"

def mesafe_hesapla(sehir_a, sehir_b):
    """
    İki Sehir nesnesi arasındaki Öklid mesafesini hesaplar.
    """
    return math.sqrt((sehir_a.x - sehir_b.x)**2 + (sehir_a.y - sehir_b.y)**2)

def dosyadan_oku(dosya_yolu):
    """
    Bir .tsp dosyasını okur, şehirleri ayrıştırır 
    ve bir Sehir nesneleri listesi döndürür.
    """
    sehirler = []
    veri_bolumu_basladi = False
    
    with open(dosya_yolu, 'r') as f:
        for satir in f:
            satir = satir.strip() 

            if satir == "EOF":
                break 
                
            if veri_bolumu_basladi:
                parcalar = satir.split()
                if len(parcalar) == 3:
                    yeni_sehir = Sehir(parcalar[0], parcalar[1], parcalar[2])
                    sehirler.append(yeni_sehir)

            if satir == "NODE_COORD_SECTION":
                veri_bolumu_basladi = True
                
    return sehirler

# --- 2. ADIM: ÇÖZÜMÜ TANIMLAMA ---

class Kromozom:
    """
    Bir çözüm adayını (turu) temsil eder.
    'genler' listesi, şehirlerin ziyaret sırasını tutar.
    'fitness' ise bu turun toplam mesafesidir.
    """
    def __init__(self, genler):
        self.genler = genler # genler, Sehir nesnelerinin bir listesidir
        self.fitness = 0.0 # Başlangıçta fitness (mesafe) 0
        self.fitness_hesapla() # Kromozom oluşur oluşmaz fitness'ını hesapla

    def __repr__(self):
        """
        Kromozomu daha okunaklı yazdırmak için.
        """
        # Sadece şehir ID'lerini gösterelim
        tur_sirasi = " -> ".join([str(sehir.id) for sehir in self.genler])
        # Fitness'ı daha net görmek için turu kısa kesebiliriz:
        if len(self.genler) > 5:
             tur_sirasi = " -> ".join([str(sehir.id) for sehir in self.genler[:3]]) + "..." + " -> ".join([str(sehir.id) for sehir in self.genler[-2:]])

        return f"[Fitness: {self.fitness:.2f}] | Tur: {tur_sirasi}"

    def fitness_hesapla(self):
        """
        Bu kromozomun (turun) toplam mesafesini (fitness) hesaplar.
        """
        toplam_mesafe = 0.0
        
        for i in range(len(self.genler) - 1):
            sehir_suanki = self.genler[i]
            sehir_sonraki = self.genler[i+1]
            toplam_mesafe += mesafe_hesapla(sehir_suanki, sehir_sonraki)
            
        sehir_son = self.genler[-1]
        sehir_ilk = self.genler[0]
        toplam_mesafe += mesafe_hesapla(sehir_son, sehir_ilk)
        
        self.fitness = toplam_mesafe
        return toplam_mesafe



# --- 3. ADIM: BAŞLANGIÇ ---

def ilk_populasyonu_olustur(tum_sehirler, populasyon_buyuklugu):
    """
    Verilen şehir listesini kullanarak rastgele karıştırılmış
    kromozomlardan oluşan bir başlangıç popülasyonu oluşturur.
    """
    populasyon = []
    
    for _ in range(populasyon_buyuklugu):
        # tum_sehirler listesini rastgele karıştırılmış BİR KOPYASINI oluştur
        # 'random.sample(liste, k)' k elemanlı rastgele bir kopya seçer.
        # k=len(liste) dersek, listenin tamamının rastgele karışık bir kopyasını alırız.
        
        # Bu yöntem, 'tum_sehirler' orijinal listesini bozmamızı engeller.
        rastgele_genler = random.sample(tum_sehirler, len(tum_sehirler))
        
        # Bu rastgele gen listesiyle yeni bir kromozom oluştur
        yeni_kromozom = Kromozom(rastgele_genler)
        
        # Yeni kromozomu popülasyona ekle
        populasyon.append(yeni_kromozom)
        
    return populasyon

def rulet_tekeri_secilimi(populasyon):
    """
    Popülasyon içinden fitness'a göre ağırlıklı (rulet tekeri) 
    bir ebeveyn seçer. (Minimizasyon problemine uyarlanmıştır).
    """
    
    # 1. Fitness'ı tersine çevir (skor oluştur)
    # En kötü (en yüksek) fitness'ı bul
    en_kotu_fitness = max(k.fitness for k in populasyon)
    
    # Her kromozom için bir ağırlık hesapla:
    # Ağırlık = (En Kötü Fitness - Kromozomun Fitness'ı) + 1
    # (+1 ekleyerek en kötü çözümün bile 0 ağırlık almasını engelleriz)
    agirliklar = []
    for kromozom in populasyon:
        # En iyi kromozom (düşük fitness) en yüksek ağırlığı alacak
        agirlik = (en_kotu_fitness - kromozom.fitness) + 1
        agirliklar.append(agirlik)
        
    # 2. Ağırlıklı rastgele seçim yap
    # 'random.choices' bu işi bizim için yapar.
    # weights=agirliklar parametresi, 'populasyon' listesindeki
    # her elemanın 'agirliklar' listesindeki karşılığına göre
    # seçilme şansını belirler. k=1 bir tane seç demektir.
    secilen_ebeveyn = random.choices(populasyon, weights=agirliklar, k=1)[0]
    
    return secilen_ebeveyn

def sira_temelli_secilim(populasyon):
    """
    Popülasyonu fitness'a göre sıralar ve bu sıraya göre
    ağırlıklı bir ebeveyn seçer. (Minimizasyon)
    """
    
    # 1. Popülasyonu fitness'a göre sırala (en iyiden en kötüye)
    # (Düşük fitness = iyi, bu yüzden 'key' normal)
    sirali_populasyon = sorted(populasyon, key=lambda k: k.fitness)
    
    # 2. Ağırlıkları oluştur (Rank (Sıra) puanları)
    # En iyi (index 0) -> N puan (örn: 100)
    # En kötü (index N-1) -> 1 puan
    # list(range(100, 0, -1)) -> [100, 99, 98, ..., 1]
    pop_boyutu = len(sirali_populasyon)
    agirliklar = list(range(pop_boyutu, 0, -1))
    
    # 3. Sıralı popülasyona ve sıra ağırlıklarına göre seçim yap
    secilen_ebeveyn = random.choices(sirali_populasyon, weights=agirliklar, k=1)[0]
    
    return secilen_ebeveyn

def cycle_crossover(ebeveyn1, ebeveyn2):
    """
    İki ebeveyn kromozoma Döngü Çaprazlaması (Cycle Crossover - CX) uygular
    ve bir çocuk kromozom döndürür.
    """
    sehir_sayisi = len(ebeveyn1.genler)
    
    # 1. Çocuğun gen listesini boş (None) olarak başlat
    cocuk_genler = [None] * sehir_sayisi
    
    # 2. Döngüleri bulmak için Ebeveyn 1'in genlerini bir 
    #    sözlüğe (map) alalım (Sehir -> Index). 
    #    Bu, arama işlemini çok hızlandırır.
    ebeveyn1_pozisyon_map = {sehir: index for index, sehir in enumerate(ebeveyn1.genler)}

    # 3. Döngüleri bul ve çocuğu oluştur
    
    # Başlangıç index'i (0) ile ilk döngüye başla
    index = 0
    while cocuk_genler[index] is None:
        # Döngüdeki elemanları Ebeveyn 1'den al
        cocuk_genler[index] = ebeveyn1.genler[index]
        
        # Ebeveyn 2'de aynı index'teki şehir hangisi?
        ebeveyn2_sehri = ebeveyn2.genler[index]
        
        # Bu şehrin Ebeveyn 1'deki pozisyonunu (index'ini) bul
        index = ebeveyn1_pozisyon_map[ebeveyn2_sehri]
        
        # Eğer bu index'teki şehir çocuğa zaten eklendiyse, döngü tamamlanmıştır.
        # Başa dön (while cocuk_genler[index] is None)

    # 4. Döngü tamamlandı. Çocuktaki tüm boş (None) yerleri
    #    Ebeveyn 2'den, aynı pozisyondan alarak doldur.
    for i in range(sehir_sayisi):
        if cocuk_genler[i] is None:
            cocuk_genler[i] = ebeveyn2.genler[i]
            
    # 5. Yeni gen listesiyle bir çocuk Kromozom nesnesi oluştur
    cocuk = Kromozom(cocuk_genler)
    return cocuk

def insert_mutasyonu(kromozom):
    """
    Kromozoma Araya Ekleme (Insert) Mutasyonu uygular.
    Bir geni (şehri) rastgele seçer ve başka bir rastgele 
    pozisyona ekler.
    
    Not: Bu fonksiyon 'kromozom' nesnesini DOĞRUDAN değiştirir.
    """
    sehir_sayisi = len(kromozom.genler)
    
    # 1. Rastgele iki pozisyon (index) seç
    # 'random.randrange(N)' 0'dan N-1'e kadar bir sayı seçer
    index_i = random.randrange(sehir_sayisi)
    index_j = random.randrange(sehir_sayisi)
    
    # İki index'in aynı olmamasını sağla (küçük bir optimizasyon)
    while index_i == index_j:
        index_j = random.randrange(sehir_sayisi)
        
    # 2. 'index_i'deki şehri al ve listeden (geçici olarak) çıkar
    # .pop(index) elemanı o index'ten çıkarır VE bize döndürür
    sehir = kromozom.genler.pop(index_i)
    
    # 3. Çıkarılan şehri 'index_j' pozisyonuna ekle
    # .insert(index, eleman) elemanı o index'e ekler, diğerlerini kaydırır
    kromozom.genler.insert(index_j, sehir)
    
    # 4. ÖNEMLİ: Genler değiştiği için fitness'ı yeniden hesapla
    kromozom.fitness_hesapla()
    
    return kromozom # Değiştirilmiş kromozomu döndür


def slide_mutasyonu(kromozom):
    """
    Kromozoma Rastgele Kaydırma (Displacement) Mutasyonu uygular.
    Rastgele bir alt-liste (blok) seçer ve bu bloğu
    turda başka bir rastgele pozisyona 'kaydırır'.
    
    Not: Bu fonksiyon 'kromozom' nesnesini DOĞRUDAN değiştirir.
    """
    sehir_sayisi = len(kromozom.genler)
    
    # 1. Rastgele bir alt-liste (blok) belirle [i...j]
    # 'random.sample(range(N), 2)' 0-N-1 arası 2 farklı sayı seçer
    indexler = sorted(random.sample(range(sehir_sayisi), 2))
    i = indexler[0]
    j = indexler[1] # j her zaman i'den büyük olacak
    
    # Alt-listeyi (bloğu) al
    blok = kromozom.genler[i : j+1] # [i...j] arasındaki şehirler
    
    # 2. Bu bloğu turdan çıkar
    # (Önce arkayı, sonra önü silmek index hatasını engeller)
    del kromozom.genler[i : j+1]
    
    # 3. Bloğu eklemek için yeni bir rastgele pozisyon seç
    # Kalan gen sayısı (N - (j-i+1)) içinde bir yer seç
    yeni_pozisyon = random.randrange(len(kromozom.genler))
    
    # 4. Bloğu yeni pozisyona yapıştır
    # 'list.insert' ile tek tek eklemek yerine, liste dilimleme 
    # ile tüm bloğu tek seferde ekleyebiliriz:
    kromozom.genler[yeni_pozisyon:yeni_pozisyon] = blok
    
    # 5. ÖNEMLİ: Genler değiştiği için fitness'ı yeniden hesapla
    kromozom.fitness_hesapla()
    
    return kromozom # Değiştirilmiş kromozomu döndür


# --- TEST KODLARI (SADECE BURASI ÇALIŞTIRILIR) ---

if __name__ == "__main__":
    
    # --- 1. Adım: Dosya Okuma Testi ---
    print("--- 1. Adım: Dosya Okuma Testi ---")
    DOSYA_ADI = "berlin52.tsp" 
    tum_sehirler = dosyadan_oku(DOSYA_ADI)
    print(f"Toplam şehir sayısı: {len(tum_sehirler)}")
    print("-" * 30) # Ayraç

    
    # --- 2. Adım: Kromozom ve Fitness Testi ---
    print("--- 2. Adım: Kromozom ve Fitness Testi ---")
    
    if tum_sehirler:
        sirasal_tur = Kromozom(tum_sehirler)
        print("Sırasal (Karıştırılmamış) Tur Kromozomu:")
        print(sirasal_tur) 
    print("-" * 30) # Ayraç

    
    # --- 3. Adım: İlk Popülasyon Testi ---
    print("--- 3. Adım: İlk Popülasyon Testi ---")
    
    POPULASYON_BUYUKLUGU = 100 # Proje 100 adet istiyor 
    
    if tum_sehirler:
        ilk_populasyon = ilk_populasyonu_olustur(tum_sehirler, POPULASYON_BUYUKLUGU)
        
        print(f"{len(ilk_populasyon)} adet rastgele kromozom oluşturuldu.")
        
        # Popülasyondaki ilk 3 kromozomu ve son 2 kromozomu yazdıralım
        print("\nPopülasyondan bazı örnekler:")
        print(ilk_populasyon[0])
        print(ilk_populasyon[1])
        print(ilk_populasyon[2])
        print("...")
        print(ilk_populasyon[-2])
        print(ilk_populasyon[-1])
        
        # En iyi ve en kötü çözümü de bulalım
        # Python'da 'min' ve 'max' fonksiyonları,
        # nesneleri 'key' parametresine göre sıralayabilir.
        en_iyi_cozum = min(ilk_populasyon, key=lambda krom: krom.fitness)
        en_kotu_cozum = max(ilk_populasyon, key=lambda krom: krom.fitness)
        
        print("\nİlk Popülasyon Analizi:")
        print(f"En İyi Çözüm (En Düşük Mesafe): {en_iyi_cozum.fitness:.2f}")
        print(f"En Kötü Çözüm (En Yüksek Mesafe): {en_kotu_cozum.fitness:.2f}")

    print("--- 4. Adım: Seçilim Operatörleri Testi ---")
    if tum_sehirler:
        ebeveyn1 = rulet_tekeri_secilimi(ilk_populasyon)
        ebeveyn2 = sira_temelli_secilim(ilk_populasyon)
        print(f"Ebeveyn 1 (Rulet): {ebeveyn1.fitness:.2f}")
        print(f"Ebeveyn 2 (Sıra): {ebeveyn2.fitness:.2f}")
    print("-" * 30) # Ayraç
    

    # --- 5. Adım: Çaprazlama (Crossover) Testi ---
    print("--- 5. Adım: Çaprazlama (Crossover) Testi ---")
    
    if 'ebeveyn1' in locals() and 'ebeveyn2' in locals():
        # Ebeveynleri çaprazla
        cocuk = cycle_crossover(ebeveyn1, ebeveyn2)
        
        print("Cycle Crossover (CX) uygulandı.")
        print("Ortaya çıkan 'Çocuk' kromozomu:")
        print(cocuk)
        
        # Doğrulama: Çocukta 52 şehir var mı? (Hiç şehir kayboldu mu?)
        # Python'da 'set' yinelenen elemanları kaldırır.
        # Eğer 'cocuk.genler' listesinde 52 EŞSİZ şehir varsa,
        # 'set'in boyutu da 52 olacaktır.
        essiz_sehir_sayisi = len(set(cocuk.genler))
        print(f"Çocuktaki gen sayısı (şehir): {len(cocuk.genler)}")
        print(f"Çocuktaki eşsiz şehir sayısı: {essiz_sehir_sayisi}")

        if essiz_sehir_sayisi == len(tum_sehirler):
            print("Çaprazlama BAŞARILI: Çocuk geçerli bir tur içeriyor.")
        else:
            print("Çaprazlama HATALI: Çocuk geçersiz (yinelenen veya eksik şehir var).")
            
    else:
        print("Çaprazlama testi için ebeveynler bulunamadı.")