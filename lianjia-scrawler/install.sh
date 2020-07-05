virtualenv venv --python=python3.6
source venv/bin/activate
pip install configparser -i https://pypi.tuna.tsinghua.edu.cn/simple
mv ./venv/lib/python3.6/site-packages/configparser.py ./venv/lib/python3.6/site-packages/ConfigParser.py
sudo yum install python3-devel -y
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
