# Kiber-Şəbəkə Qoruyucusu (Cyber-Net Defender)

Python və Pygame əsasında hazırlanmış Obyekt Yönümlü Proqramlaşdırma (OOP) komanda layihəsi.

## Oyun Haqqında
Oyunçu kiber-şəbəkəni xaotik hərəkət edən kiber-viruslardan, `+10 Coin` dronlarından və Boss dalğalarından qoruyur. Oyunda mağaza (yeni gəmilər, EMP Bomba, Mini Dronlar, 20s Firewall Qalxanı), daimi xal/coin yaddaşı (`save_data.json`) və bonus rejim/mexaniklər mövcuddur.

## İdarəetmə Düymələri
- **Sol / Sağ / Yuxarı / Aşağı Oxlar:** Hərəkət (Klassik rejimdə sağ/sol, Sideways rejimdə yuxarı/aşağı)
- **Space:** Atəş açmaq
- **Shift (Sol/Sağ):** Turbo sürət (2x)
- **E:** 20 saniyəlik Firewall Qalxanını aktivləşdirmək
- **F:** EMP Bomba buraxmaq (uyğun gəmi və bomba alındıqda)
- **TAB:** Oyun rejimini dəyişmək (Klassik Şaquli / Sideways Shooter Üfüqi)
- **ESC:** Menyuya qayıtmaq
- **Q** və ya **Pəncərənin X düyməsi:** Yadda saxlayıb çıxmaq

## İşə Salınma Qaydası
1.Python 3.13.7 quraşdırın:
https://www.python.org/ftp/python/3.13.17/python-3.13.17-amd64.exe

2. Lazımi kitabxananı quraşdırın:
   ```bash
   pip install -r requirements.txt
