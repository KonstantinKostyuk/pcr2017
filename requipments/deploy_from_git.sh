git fetch --all
git reset --hard origin/master
git pull origin master
find ~/pcr2017/ -name "*.py" | xargs chmod +x