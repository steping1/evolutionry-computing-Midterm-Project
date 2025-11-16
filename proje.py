import math
import random
import os
import sys

# --- GLOBAL DEĞİŞKENLER ---
# Mesafeleri bir kez hesaplayıp burada saklayacağız (Hız için kritik)
MESAFE_MATRISI = [] 

# --- 1. ADIM: ZEMİN HAZIRLIĞI ---

class Sehir:
    """
    .tsp dosyasındaki bir şehri (düğümü) temsil eder.
    id, x ve y koordinatlarını tutar.
    """
    def __init__(self, id, x, y):
        self.id = int(id) # ID'ler 1'den başlar
        self.x = float(x)
        self.y = float(y)

    def __repr__(self):
        return f"Sehir {self.id}"

def mesafe_hesapla_oklid(sehir_a, sehir_b):
    """
    Gerçek Öklid mesafesini hesaplar.
    Bunu SADECE programın başında matrisi doldururken kullanacağız.
    """
    return math.sqrt((sehir_a.x - sehir_b.x)**2 + (sehir_a.y - sehir_b.y)**2)

def matrisi_doldur(sehirler):
    """
    Tüm şehirler arası mesafeleri hesaplayıp global bir matrise kaydeder.
    Bu işlem O(N^2) sürer ama sonraki milyarlarca sorguyu O(1) yapar.
    """
    global MESAFE_MATRISI
    boyut = len(sehirler)
    # ID'ler 1'den başladığı için erişim kolaylığı adına ID'leri index olarak kullanacağız.
    # Bu yüzden şehir sayısı kadar (0'dan N-1'e) bir matris oluşturuyoruz.
    # Şehir ID'sine erişirken -1 yapacağız.
    
    MESAFE_MATRISI = [[0.0] * boyut for _ in range(boyut)]
    
    # Sehir listesindeki sıraya göre matrisi doldur
    for i in range(boyut):
        for j in range(boyut):
            dist = mesafe_hesapla_oklid(sehirler[i], sehirler[j])
            # sehirler[i].id kullanmak yerine listenin indexini kullanıyoruz
            # Çünkü sehirler listesi zaten sıralı okunuyor.
            MESAFE_MATRISI[sehirler[i].id - 1][sehirler[j].id - 1] = dist
            
    print(f"-> {boyut}x{boyut} boyutunda Mesafe Matrisi önceden hesaplandı (RAM'e yüklendi).")

def hizli_mesafe_al(sehir_a, sehir_b):
    """
    Matristen hazır hesaplanmış mesafeyi ışık hızında çeker.
    """
    global MESAFE_MATRISI
    # ID'ler 1 tabanlı, liste indexleri 0 tabanlı olduğu için -1 çıkarıyoruz
    return MESAFE_MATRISI[sehir_a.id - 1][sehir_b.id - 1]

def dosyadan_oku(dosya_yolu):
    """
    Bir .tsp dosyasını okur, şehirleri ayrıştırır.
    """
    sehirler = []
    veri_bolumu_basladi = False
    
    if not os.path.exists(dosya_yolu):
        return []

    with open(dosya_yolu, 'r') as f:
        for satir in f:
            satir = satir.strip() 
            if satir == "EOF": break 
                
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
    """
    def __init__(self, genler):
        self.genler = genler 
        self.fitness = 0.0 
        self.fitness_hesapla() # Oluşur oluşmaz hesapla

    def __repr__(self):
        tur_sirasi = " -> ".join([str(sehir.id) for sehir in self.genler])
        if len(self.genler) > 5:
             tur_sirasi = " -> ".join([str(sehir.id) for sehir in self.genler[:3]]) + "..." + " -> ".join([str(sehir.id) for sehir in self.genler[-2:]])
        return f"[Fitness: {self.fitness:.2f}] | Tur: {tur_sirasi}"
    
    def kopyala(self):
        gen_kopyasi = self.genler[:] 
        return Kromozom(gen_kopyasi)

    def fitness_hesapla(self):
        """
        Bu kromozomun (turun) toplam mesafesini HIZLI matris ile hesaplar.
        """
        toplam_mesafe = 0.0
        uzunluk = len(self.genler)
        
        for i in range(uzunluk):
            sehir_suanki = self.genler[i]
            # Modülo operatörü (%) ile son şehri ilk şehre bağlarız
            sehir_sonraki = self.genler[(i + 1) % uzunluk]
            
            # BURASI DEĞİŞTİ: Karekök yerine matristen okuyoruz
            toplam_mesafe += hizli_mesafe_al(sehir_suanki, sehir_sonraki)
        
        self.fitness = toplam_mesafe
        return toplam_mesafe

# --- 3. ADIM: BAŞLANGIÇ POPÜLASYONU ---

def ilk_populasyonu_olustur(tum_sehirler, populasyon_buyuklugu):
    populasyon = []
    for _ in range(populasyon_buyuklugu):
        rastgele_genler = random.sample(tum_sehirler, len(tum_sehirler))
        yeni_kromozom = Kromozom(rastgele_genler)
        populasyon.append(yeni_kromozom)
    return populasyon

# --- 4. ADIM: SEÇİLİM OPERATÖRLERİ ---

def rulet_tekeri_secilimi(populasyon):
    en_kotu_fitness = max(k.fitness for k in populasyon)
    agirliklar = []
    for kromozom in populasyon:
        agirlik = (en_kotu_fitness - kromozom.fitness) + 1
        agirliklar.append(agirlik)
    secilen_ebeveyn = random.choices(populasyon, weights=agirliklar, k=1)[0]
    return secilen_ebeveyn

def sira_temelli_secilim(populasyon):
    sirali_populasyon = sorted(populasyon, key=lambda k: k.fitness)
    pop_boyutu = len(sirali_populasyon)
    agirliklar = list(range(pop_boyutu, 0, -1))
    secilen_ebeveyn = random.choices(sirali_populasyon, weights=agirliklar, k=1)[0]
    return secilen_ebeveyn

# --- 5. ADIM: ÇAPRAZLAMA (CROSSOVER) ---

def cycle_crossover(ebeveyn1, ebeveyn2):
    sehir_sayisi = len(ebeveyn1.genler)
    cocuk_genler = [None] * sehir_sayisi
    
    # Hız optimizasyonu: Şehir nesnesini anahtar olarak kullan
    ebeveyn1_pozisyon_map = {sehir: index for index, sehir in enumerate(ebeveyn1.genler)}

    index = 0
    while cocuk_genler[index] is None:
        cocuk_genler[index] = ebeveyn1.genler[index]
        ebeveyn2_sehri = ebeveyn2.genler[index]
        index = ebeveyn1_pozisyon_map[ebeveyn2_sehri]

    for i in range(sehir_sayisi):
        if cocuk_genler[i] is None:
            cocuk_genler[i] = ebeveyn2.genler[i]
            
    cocuk = Kromozom(cocuk_genler)
    return cocuk

# --- 6. ADIM: MUTASYON OPERATÖRLERİ ---

def insert_mutasyonu(kromozom):
    sehir_sayisi = len(kromozom.genler)
    if sehir_sayisi < 2: return
    
    index_i = random.randrange(sehir_sayisi)
    index_j = random.randrange(sehir_sayisi)
    while index_i == index_j:
        index_j = random.randrange(sehir_sayisi)
        
    sehir = kromozom.genler.pop(index_i)
    kromozom.genler.insert(index_j, sehir)
    kromozom.fitness_hesapla()

def slide_mutasyonu(kromozom):
    sehir_sayisi = len(kromozom.genler)
    if sehir_sayisi < 2: return

    indexler = sorted(random.sample(range(sehir_sayisi), 2))
    i = indexler[0]
    j = indexler[1]
    
    blok = kromozom.genler[i : j+1]
    del kromozom.genler[i : j+1]
    
    # Düzeltilmiş mantık (Boş liste hatasını önlemek için +1)
    yeni_pozisyon = random.randrange(len(kromozom.genler) + 1)
    
    kromozom.genler[yeni_pozisyon:yeni_pozisyon] = blok
    kromozom.fitness_hesapla()

# --- BONUS ADIMLARI: 2-OPT ve 3-OPT (HIZLANDIRILMIŞ) ---

def iki_opt(kromozom):
    """
    2-opt optimizasyonu. Hızlandırılmış matris kullanımı ile.
    """
    yeni_krom = kromozom.kopyala()
    genler = yeni_krom.genler
    N = len(genler)
    iyilesme = True
    
    while iyilesme:
        iyilesme = False
        for i in range(N - 2):
            A = genler[i]
            B = genler[i+1]
            for j in range(i + 2, N - 1): # Wrap-around ihmali (basitlik için N-1)
                C = genler[j]
                D = genler[j+1]
                
                # Matristen çek (HIZLI)
                eski_dist = hizli_mesafe_al(A, B) + hizli_mesafe_al(C, D)
                yeni_dist = hizli_mesafe_al(A, C) + hizli_mesafe_al(B, D)
                
                if yeni_dist < eski_dist:
                    genler[i+1 : j+1] = reversed(genler[i+1 : j+1])
                    iyilesme = True
                    # First Improvement: Bulduğunda dön
                    break 
            if iyilesme: break
            
    yeni_krom.fitness_hesapla()
    return yeni_krom

def uc_opt(kromozom):
    """
    3-opt optimizasyonu. 
    Matris kullanımı sayesinde O(N^3) olmasına rağmen çok daha hızlı çalışacaktır.
    """
    yeni_krom = kromozom.kopyala()
    genler = yeni_krom.genler
    N = len(genler)
    iyilesme = True
    
    # Sonsuz döngü riskine karşı tur limiti
    max_tur = 50 
    tur_sayisi = 0

    while iyilesme and tur_sayisi < max_tur:
        iyilesme = False
        tur_sayisi += 1
        
        for i in range(N - 4):
            for j in range(i + 2, N - 2):
                for k in range(j + 2, N - 1): # k, N-1'e kadar (Wrap-around basitleştirme)
                    
                    k_next = k + 1
                    
                    # Kenar noktaları
                    A, B = genler[i], genler[i+1]
                    C, D = genler[j], genler[j+1]
                    E, F = genler[k], genler[k_next]
                    
                    # Mevcut mesafe (sadece 3 kenar) - MATRİSTEN OKU
                    d0 = hizli_mesafe_al(A,B) + hizli_mesafe_al(C,D) + hizli_mesafe_al(E,F)
                    
                    # Olası 7 hamle için mesafeler (matristen çekildiği için çok hızlı)
                    # 2-opt hamleleri
                    d1 = hizli_mesafe_al(A,C) + hizli_mesafe_al(B,D) + hizli_mesafe_al(E,F)
                    d2 = hizli_mesafe_al(A,B) + hizli_mesafe_al(C,E) + hizli_mesafe_al(D,F)
                    d3 = hizli_mesafe_al(A,E) + hizli_mesafe_al(D,F) + hizli_mesafe_al(C,B)
                    # 3-opt hamleleri
                    d4 = hizli_mesafe_al(A,C) + hizli_mesafe_al(B,E) + hizli_mesafe_al(D,F)
                    d5 = hizli_mesafe_al(A,E) + hizli_mesafe_al(D,B) + hizli_mesafe_al(C,F)
                    d6 = hizli_mesafe_al(A,D) + hizli_mesafe_al(C,E) + hizli_mesafe_al(B,F)
                    d7 = hizli_mesafe_al(A,D) + hizli_mesafe_al(C,F) + hizli_mesafe_al(B,E)

                    move = 0
                    # En iyi iyileştirmeyi bul (Greedy)
                    if d1 < d0: move = 1; d0 = d1
                    if d2 < d0: move = 2; d0 = d2
                    if d3 < d0: move = 3; d0 = d3
                    if d4 < d0: move = 4; d0 = d4
                    if d5 < d0: move = 5; d0 = d5
                    if d6 < d0: move = 6; d0 = d6
                    if d7 < d0: move = 7; d0 = d7

                    if move > 0:
                        # Hamleyi uygula (Liste dilimleme işlemleri)
                        if move == 1: genler[i+1:j+1] = reversed(genler[i+1:j+1])
                        elif move == 2: genler[j+1:k+1] = reversed(genler[j+1:k+1])
                        elif move == 3: genler[i+1:k+1] = reversed(genler[i+1:k+1])
                        elif move == 4: genler[i+1:k+1] = genler[j+1:k+1] + genler[i+1:j+1]
                        elif move == 5: genler[i+1:k+1] = list(reversed(genler[i+1:j+1])) + list(reversed(genler[j+1:k+1]))
                        elif move == 6: genler[i+1:k+1] = list(reversed(genler[j+1:k+1])) + genler[i+1:j+1]
                        elif move == 7: genler[i+1:k+1] = genler[j+1:k+1] + list(reversed(genler[i+1:j+1]))
                        
                        iyilesme = True
                        break # First Improvement: İç döngüden çık
                if iyilesme: break
            if iyilesme: break
            
    yeni_krom.fitness_hesapla()
    return yeni_krom


# --- 7. ANA ALGORİTMA DÖNGÜSÜ ---

if __name__ == "__main__":
    
    # 1. Dosyayı Belirle
    DOSYA_ADI = "berlin52.tsp"
    
    # 2. Dosyayı Oku
    tum_sehirler = dosyadan_oku(DOSYA_ADI)
    if not tum_sehirler:
        print(f"HATA: '{DOSYA_ADI}' dosyası bulunamadı.")
        print("Lütfen dosyanın bu python dosyasıyla aynı klasörde olduğundan emin olun.")
        sys.exit()

    # 3. KRİTİK ADIM: MATRİSİ DOLDUR (Bu olmazsa çok yavaşlar)
    matrisi_doldur(tum_sehirler)

    # 4. Parametreler
    POPULASYON_BUYUKLUGU = 100
    NESIL_SAYISI_LIMITI = 100            
    IYILESME_OLMAYAN_LIMIT = 5          

    print("\n--- Evrimsel Algoritma Başlatılıyor ---")
    print(f"Problem: {DOSYA_ADI}")
    print(f"Popülasyon Büyüklüğü: {POPULASYON_BUYUKLUGU}")
    print("-" * 40)
        
    # 5. GA Başlat
    mevcut_populasyon = ilk_populasyonu_olustur(tum_sehirler, POPULASYON_BUYUKLUGU)
    global_en_iyi = min(mevcut_populasyon, key=lambda k: k.fitness).kopyala()
    
    iyilesmeyen_nesil_sayisi = 0

    # 6. İterasyonlar
    for nesil_no in range(1, NESIL_SAYISI_LIMITI + 1):
        
        bu_neslin_en_iyisi = min(mevcut_populasyon, key=lambda k: k.fitness)
        
        if bu_neslin_en_iyisi.fitness < global_en_iyi.fitness:
            global_en_iyi = bu_neslin_en_iyisi.kopyala() 
            iyilesmeyen_nesil_sayisi = 0
        else:
            iyilesmeyen_nesil_sayisi += 1
        
        print(f"Nesil {nesil_no:3} | En İyi Mesafe: {global_en_iyi.fitness:<10.2f} | (İyileşmeyen: {iyilesmeyen_nesil_sayisi})")
        
        if iyilesmeyen_nesil_sayisi >= IYILESME_OLMAYAN_LIMIT:
            print(f"\nSonlanma: {IYILESME_OLMAYAN_LIMIT} nesildir iyileşme olmadı.")
            break
        
        # Yeni Nesil Üretimi
        yeni_populasyon = []
        yeni_populasyon.append(global_en_iyi.kopyala()) # Elitizm
        
        while len(yeni_populasyon) < POPULASYON_BUYUKLUGU:
            if len(yeni_populasyon) <= (POPULASYON_BUYUKLUGU / 2):
                e1, e2 = sira_temelli_secilim(mevcut_populasyon), sira_temelli_secilim(mevcut_populasyon)
            else:
                e1, e2 = rulet_tekeri_secilimi(mevcut_populasyon), rulet_tekeri_secilimi(mevcut_populasyon)
            
            cocuk = cycle_crossover(e1, e2)
            
            if random.random() < 0.5: insert_mutasyonu(cocuk)
            else: slide_mutasyonu(cocuk)
            
            yeni_populasyon.append(cocuk)
            
        mevcut_populasyon = yeni_populasyon
    
    # 7. Sonuçlar
    print("-" * 40)
    print("Evrimsel Algoritma Tamamlandı.")
    print(f"GA Sonucu (2-opt öncesi) En İyi Mesafe: {global_en_iyi.fitness:.2f}")

    # 8. Bonus: 2-opt
    print("\n--- 2-Opt (Bonus) İyileştirmesi Başlatılıyor ---")
    print("(Hızlı çalışıyor...)")
    iki_opt_sonucu = iki_opt(global_en_iyi)
    print(f"2-Opt Sonucu En İyi Mesafe: {iki_opt_sonucu.fitness:.2f}")

    # 9. Bonus: 3-opt
    print("\n--- 3-Opt (Bonus) İyileştirmesi Başlatılıyor ---")
    print("(Optimize edildi, hızlı çalışacak...)")
    uc_opt_sonucu = uc_opt(iki_opt_sonucu)
    
    print("\n--- Nihai Sonuç (3-opt Sonrası) ---")
    print(f"Bulunan en iyi mesafe (fitness): {uc_opt_sonucu.fitness:.2f}")
    print("En iyi tur (ID sırası):")
    
    tur_sirasi_listesi = [str(sehir.id) for sehir in uc_opt_sonucu.genler]
    for i in range(0, len(tur_sirasi_listesi), 15):
        print(" -> ".join(tur_sirasi_listesi[i:i+15]))
    print("-" * 40)