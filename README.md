# Mersin otobüs kayıt
Geçmişte otobüslerin bulunduğu yerlerini gösteren basit bir site.

Python Flask ile çalışır.

Her 5 dakikada bir https://ulasim.mersin.bel.tr/hattakiaraclar.php adresinden otobüslerin anlık yerlerini ve duraklarını, **araclar-zamanlar.db** adlı *sqlite3* veritabanına kaydeder. Daha sonra bir web tarayıcıdan **localhost**'a girilerek geçmiş kayıtlara ulaşılabilir.

### Gereksinimleri kurma:

`pip install -r requirements.txt`

### Çalıştırma

`flask run` veya `python app.py`
