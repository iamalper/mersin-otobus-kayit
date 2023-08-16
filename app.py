import requests as r
from flask import Flask, render_template, redirect, abort
from flask_apscheduler import APScheduler
import sqlite3 as sl
from time import strftime, strptime, mktime, localtime

url="https://ulasim.mersin.bel.tr/ajax/bilgi.php"
pem="mersin-bel-tr-chain.pem"

app = Flask(__name__)
app.secret_key="897eff18d43abd640558688d4b11a48bda4346f921dd401a3f6c52920493491a"

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

with sl.connect('araclar-zamanlar.db') as con:
	con.execute("CREATE TABLE IF NOT EXISTS hat_kayitlari (tarih_saat datetime not null, hat varchar(5) not null, enlem int not null, boylam int not null)")
	con.commit()

def tumhatlar():
	response=r.post(url,data={"aranan":"TUM","tipi":"hatbilgisi"},verify=pem)
	assert response.status_code==200, "Http hatası: %i" %(response.status_code)
	return response.json()

#tip [hattakiaraclar, hatdurak]
def hatbilgisi(hatno,tip):
	response=r.post(url,data={"hatno":hatno,"tipi":tip},verify=pem)
	assert response.status_code==200, "Http hatası: %i" %(response.status_code)
	try:
		resjson=response.json()
	except r.exceptions.JSONDecodeError:
		return 0
	return resjson

def hatkayit():
	con = sl.connect('araclar-zamanlar.db')
	print("Kayıt başladı")
	hatlar=tumhatlar()
	saatstr=strftime('%Y-%m-%d %H:%M:00')
	print("Zaman: %s"%(saatstr))
	execlist=[]
	for x in hatlar:
		hat=f'{x["hat_no"]["0"]}-{x["hat_yon"]["0"]}'
		#print("%s bilgisi alınıyor" %(hat))
		araclar=hatbilgisi(hat,"hattakiaraclar")
		if araclar != 0:
			for x in araclar:
				enlem=x["enlem"]["0"]
				boylam=x["boylam"]["0"]
				execlist.append((saatstr,hat,enlem,boylam))
	con.executemany(" INSERT INTO hat_kayitlari (tarih_saat,hat,enlem,boylam) VALUES (?,?,?,?)",execlist)
	con.commit()
	con.close()
	print("Kayıt tamam")

scheduler.add_job(id='hat_kaydet', func=hatkayit, trigger='cron', minute='*/5')

@app.route("/api/hatlar", methods=['GET'])
def hatlar():
	hatlar=tumhatlar()
	hatlist=[]
	for x in hatlar:
		hatlist.append({"Hatno":x["hat_no"]["0"],"Hatyon":x["hat_yon"]["0"]})
	return hatlist

@app.route("/api/hattakiaraclar/<hat>/<int:zamanint>", methods=['GET'])
def hattakiaraclar(hat,zamanint):
	con = sl.connect('araclar-zamanlar.db')
	tarihsaat=strftime('%Y-%m-%d %H:%M:00',localtime(zamanint))
	res = con.execute("SELECT enlem,boylam FROM hat_kayitlari WHERE (tarih_saat=? AND hat=?)",(tarihsaat,hat))
	cords=res.fetchall()
	con.close()
	return cords

@app.route("/api/zamanlar", methods=['GET'])
def zamanlar():
	con = sl.connect('araclar-zamanlar.db')
	res = con.execute("SELECT tarih_saat FROM hat_kayitlari")
	sqlzamanlar=res.fetchall()
	con.close()
	zamanlar=[]
	for x in sqlzamanlar:
		inttime=int(mktime(strptime(x[0],'%Y-%m-%d %H:%M:00')))
		if [x[0],inttime] not in zamanlar:
			zamanlar.append([x[0],inttime])
	return zamanlar

@app.route("/api/duraklar/<hat>", methods=['GET'])
def duraklar(hat):
	duraklarresponse=hatbilgisi(hat,"hatdurak")
	duraklar=[]
	for x in duraklarresponse:
		enlem=x["enlem"]["0"]
		boylam=x["boylam"]["0"]
		duraklar.append([enlem,boylam])
	return duraklar

@app.route("/")
def main():
	
	return render_template("main.html")

@app.errorhandler(404)
def page_not_found(error):
    return '404',404

if __name__ == "__main__":
	app.run()