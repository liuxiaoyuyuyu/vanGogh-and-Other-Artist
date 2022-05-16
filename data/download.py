from multiprocessing import Pool
import platform,multiprocessing
import shutil
import os
import glob
import pandas as pd
import numpy
from tqdm import tqdm
import hashlib
import wget

def download(info):
	infos = info.split('|')
	if len(infos) != 2:
		return
	else:
		url = infos[0]
		out = infos[1]
		wget.download(url,out = out)


def wikiArtsDownload():
	os.system("kaggle datasets download -d antoinegruson/-wikiart-all-images-120k-link")

	# Output
	output_path = "./subWikiArts"
	if not os.path.isdir(output_path):
		os.mkdir(output_path)

	outputImg_path = "./subWikiArts/imgs"
	if not os.path.isdir(outputImg_path):
		os.mkdir(outputImg_path)

	# List all wikiarts plots
	tmp_path = "./tmp"
	if not os.path.isdir(tmp_path):
		os.mkdir(tmp_path)
	wikiartsZip = '-wikiart-all-images-120k-link.zip'
	try:
		shutil.unpack_archive(wikiartsZip,tmp_path)
	except Exception as err:
		print(err)

	WikiArtsMeta = tmp_path+"/wikiart_scraped.csv"
	WikiArts = pd.read_csv(WikiArtsMeta)

	# List of Artist to retrive:
	Artists = ["Leonardo da Vinci","Rembrandt","Pablo Picasso","Salvador Dali"]

	WikiArtList = []
	WikiArtDF = pd.DataFrame()
	for artist in Artists:
		WikiArtDF = pd.concat([WikiArtDF, WikiArts[WikiArts["Artist"] == artist]])

	URLlinks = WikiArtDF["Link"].values
	hashList = []
	downloadArg = []
	hashName = "h3f34f384fhf239f"
	for link in URLlinks:
		hashName = hashlib.md5((link+hashName).encode()).hexdigest()
		hashList.append(hashName)
		downloadArg.append(link+"|"+tmp_path+"/"+hashName+".jpg")
	
	WikiArtDF["hash"] = hashList

	pool = Pool(processes=8)
	for _ in tqdm(pool.imap_unordered(download, downloadArg),total=len(downloadArg)):
		pass

	for ihash in tqdm(range(len(downloadArg))):
		fileName = downloadArg[ihash].split("|")[-1]
		hashName = hashList[ihash]
		shutil.move(fileName, outputImg_path + "/" + hashName + ".jpg", copy_function = shutil.copy2)

	WikiArtDF.to_csv(output_path + "/WikiArts.csv")


if __name__ == "__main__":
	if platform.system() == "Darwin":
		multiprocessing.set_start_method('spawn')
	
	wikiArtsDownload()



