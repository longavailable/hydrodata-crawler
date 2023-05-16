rm -rf data

git clone https://github.com/longavailable/hydrodata data

/root/.homeassistant/bin/python 002-hydrodata-download-ahsxx-datong.py

cd data

git add .
git diff-index --quiet HEAD || git commit -m "Update hydrodata(#datong) from Cron `date`" && git push
