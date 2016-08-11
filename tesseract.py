import os,subprocess

def image_to_string(img, cleanup = True):
# cleanup为True则识别完成后删除生成的文本文件
	
	child = subprocess.Popen(['tesseract', img, 'output'], stdout=subprocess.PIPE, stderr=subprocess.PIPE) #生成output.txt文件
	child.wait()
	text = open('output.txt').read().strip()
	if cleanup:
		os.remove('output.txt')
	print(text)
	return text

