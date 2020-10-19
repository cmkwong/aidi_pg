source activate
source deactivate
conda create --name aidi -y python==3.7.5
conda activate aidi
conda install -y -c anaconda jupyter
conda install -y -c conda-forge jupyter_contrib_nbextensions
conda install -y -c conda-forge selenium
conda install -y numpy==1.16.6
conda install -y pandas==1.0.3
conda install -y -c anaconda beautifulsoup4
conda install -y -c anaconda dnspython
conda install -y -c anaconda pymongo
pip install appscript
pip install pyTelegramBotAPI
