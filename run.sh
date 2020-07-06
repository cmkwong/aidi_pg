source activate
source deactivate
conda activate aidi
cd ~/Desktop/aidi_pg/code
git fetch https://github.com/cmkwong/aidi_pg.git master
git reset --hard FETCH_HEAD
git clean -df
python main.py
