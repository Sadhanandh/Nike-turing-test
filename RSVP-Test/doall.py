import glob
import sortme
gl = glob.glob("*.jpg")
wrong = 0
right = 0
for x in gl:
	text=sortme.mainer(x)
	if text == None:
		wrong+=1
	else:
		right+=1

print "Hit Rate:" ,right,"/",len(gl)
