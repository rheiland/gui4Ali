
python params_run.py myproj params_run.txt
montage -geometry +0+0  -tile 2x2 run1/final.svg run2/final.svg run3/final.svg run4/final.svg   tmp.jpg
convert -resize 25% tmp.jpg tmp25.jpg


