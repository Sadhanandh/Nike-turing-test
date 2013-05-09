import cv2
import numpy
import sys
import os
import math
import pytesser.pytesser as pt

def parallelh(mlist,delta):
	match = 0
	f = []
	list_ = mlist
	donel = []
	for n,x in enumerate (list_):
		for m,y in enumerate(list_):
			if m in donel:
				continue
			if not numpy.array_equal(x,y):
				start = min(x[0],x[2])
				xstart = min(y[0],y[2])
				end = max(x[0],x[2])
				xend = max(y[0],y[2])
				for c in range(start,end):
					for v in range(xstart,xend):
						if c == v:
							match+=1
				f.append((n,m,match))
				match =0
		donel.append(n)
	return f

def parallelv(mlist,delta):
	match = 0
	f = []
	list_ = mlist
	donel = []
	for n,x in enumerate (list_):
		for m,y in enumerate(list_):
			if m in donel:
				continue
			if not numpy.array_equal(x,y):
				start = min(x[1],x[3])
				xstart = min(y[1],y[3])
				end = max(x[1],x[3])
				xend = max(y[1],y[3])
				for c in range(start,end):
					for v in range(xstart,xend):
						if c == v:
							match+=1
				f.append((n,m,match))
				match =0
		donel.append(n)
	return f




def mainer(filen = "one.jpg",show = True):

	try:
		img = cv2.imread(filen)
		img = cv2.GaussianBlur(img,(3,3),0)
		gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
		graye = cv2.Canny(gray, 100, 300)
		#cv2.imshow("one2",graye)
		#cv2.imwrite("temp.jpg",graye)

		tresh = 5
		ltresh = 10
		tup = None

		lines = cv2.HoughLinesP(graye, 1, math.pi, 2, None, 25, 1);
		vlines = sorted(lines[0],key = lambda x: x[0])

		rmarray = []
		for x in range(len(vlines)):
			if x<len(vlines)-1:
				if vlines[x][0] > (vlines[x+1][0] - tresh ):
					if vlines[x][1] > vlines[x+1][1] - ltresh:
						if abs(vlines[x][3]-vlines[x][1]) > abs(vlines[x+1][3]-vlines[x+1][1]) :
							rmarray.append(vlines[x+1])
						else :
							rmarray.append(vlines[x])
		for r in rmarray:
			for n,v in enumerate(vlines):
				if numpy.array_equal(r,v):
					del vlines[n]

		for line in vlines:
			pt1 = (line[0],line[1])
			pt2 = (line[2],line[3])
			cv2.line(img, pt1, pt2, (0,0,255), 3)

		lines = cv2.HoughLinesP(graye, 1, math.pi/2, 2, None, 40, 1);
		hlines = sorted(lines[0],key = lambda x: x[1])

		rmarray = []
		for x in range(len(hlines)):
			if x<len(hlines)-1:
				if hlines[x][1] > (hlines[x+1][1] - tresh ):
					if hlines[x][0] > hlines[x+1][0] - ltresh:
						if abs(hlines[x][2]-hlines[x][0]) > abs(hlines[x+1][2]-hlines[x+1][0]) :
							rmarray.append(hlines[x+1])
						else :
							rmarray.append(hlines[x])
		for r in rmarray:
			for n,v in enumerate(hlines):
				if numpy.array_equal(r,v):
					del hlines[n]
		for line in hlines:
			pt1 = (line[0],line[1])
			pt2 = (line[2],line[3])
			cv2.line(img, pt1, pt2, (0,0,255), 3)

		hp =  parallelh(hlines,10)
		vp = parallelv(vlines,10)
		hp = sorted(hp,key = lambda x:x[2])
		vp = sorted(vp,key = lambda x:x[2])
		trsh = 10
		ltrsh = 10
		for h in vp:
			bmin = min(vlines[h[0]][0],vlines[h[1]][0])
			bmax = max(vlines[h[0]][0],vlines[h[1]][0])
			lmin = min(min(vlines[h[0]][1],vlines[h[0]][3]),min(vlines[h[1]][1],vlines[h[1]][3]))
			lmax = max(max(vlines[h[0]][1],vlines[h[0]][3]),max(vlines[h[1]][1],vlines[h[1]][3]))
			for hv in hlines:
				if hv[1] > lmin -30 and hv[1]  < lmax +30:
					tup = (min(bmax,bmin)+ltrsh,lmin-trsh,max(bmax,bmin)-ltrsh,lmax+trsh)
		if tup ==None:
			print "Lines try"

			for h in hp:
				bmin = min(min(hlines[h[0]][0],hlines[h[0]][2]),min(hlines[h[1]][0],hlines[h[1]][2]))
				bmax = max(max(hlines[h[0]][0],hlines[h[0]][2]),max(hlines[h[1]][0],hlines[h[1]][2]))
				lmin = min(hlines[h[0]][1],hlines[h[1]][1])
				lmax = max(hlines[h[0]][1],hlines[h[1]][1])
				trsh = 10
				ltrsh = 10
				for hv in vlines:
					if hv[0] > bmin -30 and hv[0]  < bmax +30:
						tup = (min(bmax,bmin) - ltrsh,lmin+trsh,max(bmax,bmin)+ltrsh,lmax - trsh)
		pt1 = (tup[0],tup[1])
		pt2 = (tup[2],tup[3])
		cv2.line(img, pt1, pt2, (0,255,0), 3)
		left = tup[0]
		top = tup[1]
		new_width = tup[2]-tup[0]
		new_height = tup[3]-tup[1]


		img0 = cv2.cv.LoadImage(filen, 1)
		img1 = cv2.cv.CloneImage(img0)
		cropped = cv2.cv.CreateImage( (new_width, new_height), 8, 3)
		src_region = cv2.cv.GetSubRect(img1, (left, top, new_width, new_height) )
		cv2.cv.Copy(src_region, cropped)
		cv2.cv.SaveImage("a.png",cropped)
		dtext = pt.image_file_to_string(os.path.join(os.path.abspath("."),"a.png"))
		dtext = dtext.strip("\n").strip().replace(" ","")
		print dtext
		if show == True:
			cv2.imshow("one",img)
			cv2.waitKey(0)
		if dtext.find("#")!=0:
			print "Error!!"
			return None
		else:
			return dtext
	except TypeError :
		return None


if __name__ == "__main__":
	filen = "one.jpg"
	if len(sys.argv)>1:
		filen = sys.argv[1]
	mainer(filen)
