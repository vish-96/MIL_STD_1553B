import xml.etree.ElementTree as ET
import math
from xml.etree import ElementTree

from lxml import etree

from xml.dom import minidom

tree = ET.parse('xmlB1-periodique.xml')
root = tree.getroot()
C=[]
mess=[]
trans_delay=[]	
period=[]
dict_msg={}
low_prio_list=[]
high_prio_list=[]
e2e_delay=[]
access_delay=[]
schd_test=[]
def set_msg_lower_prio(cur_period,a):
	p=[]
	for i in range(0,len(a)):
		if (a[i][1][0]>cur_period):
			p.append(a[i])
	return p

def set_msg_higher_prio(cur_period,a):
	p=[]
	for i in range(0,len(a)):
		if (a[i][1][0]<=cur_period):
			p.append(a[i])
	return p

def max_Cj(list1):
	max1=0
	for i in range(0, len(list1)):
		if (list1[i][1][1]>max1):
			max1=list1[i][1][1];
	return max1	
	
def end2end(C_i,max_cj,high_prio_list):
	W=[]
	W.append(C_i+max_cj)
	i=1
	while(1):
		sum2=0
		for j in range(0, len(high_prio_list)):
			sum2=sum2+high_prio_list[j][1][1]*math.ceil(W[i-1]/high_prio_list[j][1][0])
		W.append(C_i+max_cj+ sum2)
		i=i+1
		if(W[i-1]==W[i-2]):
			return W[i-1]
	
def create_xml(root, a, trans_delay, access_delay, e2e_delay, schd_test):
	# create XML 
	tree_o = ElementTree.ElementTree()
	root_o = etree.Element('Output_file')
	#root.append(etree.Element('message'))
	
	# another child with text
	for i in range(0, len(a)):
		message = etree.Element('message')
		root_o.append(message)
		name=etree.Element('Name')
		name.text=str(root[a[i][0]][0].text)
		message.append(name)
		
		dt=etree.Element('DT')
		dt.text=str(trans_delay[a[i][0]])
		message.append(dt)
		
		dmac=etree.Element('DMAC')
		dmac.text=str(access_delay[i])
		message.append(dmac)
		
		dbeb=etree.Element('DBEB')
		dbeb.text=str(e2e_delay[i])
		message.append(dbeb)
		
		test=etree.Element('Test')
		test.text=str(schd_test[i])
		message.append(test)

	# pretty string
	print(etree.tostring(root_o, pretty_print=True))
	tree_o._setroot(root_o)
	tree_o.write("output_lab1_vishal.xml")
	print("output xml generated")

	
	
		
	
def main():  
	#print (root[0][0].text)
	min_period=10**3/float(root[0][2].text)
	for i in range (0, len(root)):
		if (min_period >float(10**3/float(root[i][2].text))):
			min_period =float(10**3/float(root[i][2].text))
		if root[i][4].text == 'SXJJ':
			print("message "+str(i))
			print ("master "+ root[i][4].text+ " sent ")
			mess.append(20*float(root[i][3].text) +56) 
			trans_delay.append(float(mess[i]/10**3))
			C.append(mess[i]/10**3)
			period.append(10**3/float(root[i][2].text))
			print (str(mess[i]) + " bits to slave "+ root[i][5].text)
			print("transmission delay: "+ str(trans_delay[i])+" ms")
			print("period: "+ str(period[i]) + "ms")
			print("C: "+ str(C[i]) + "ms")
			#assign msg's capacity and period to a dictionary
			dict_msg[i]= [period[i] , C[i]] 
		elif root[i][5].text == 'SXJJ':
			print("message "+str(i))
			print ("slave "+ root[i][4].text+ " sent ")
			mess.append(20*float(root[i][3].text) +56)#20 because we need to convert the words into bytes
			trans_delay.append(float(mess[i]/10**3))
			C.append(mess[i]/10**3)
			period.append(10**3/float(root[i][2].text))
			print (str(mess[i])+ " bits to master "+ root[i][5].text)
			print("transmission delay: "+ str(trans_delay[i])+" ms")
			print("period: "+ str(period[i]) + "ms")
			print("C: "+ str(C[i]) + "ms")
			dict_msg[i]= [period[i] , C[i]] 
		else:
			print("message "+str(i))
			print ("slave "+ root[i][4].text+ " sent ")
			mess.append(20*float(root[i][3].text)+106)
			trans_delay.append(float(mess[i]/10**3))
			C.append(mess[i]/10**3)
			period.append(10**3/float(root[i][2].text))
			print (str(mess[i])+ " bits to slave "+ root[i][5].text)
			print("transmission delay: "+ str(trans_delay[i])+" ms")
			print("period: "+ str(period[i]) + "ms")
			print("C: "+ str(C[i])+ "ms")
			dict_msg[i]= [period[i] , C[i]] 
		print("-----\n")
		
	sum_C=0	
	for i in range(0, len(C)):
		sum_C=sum_C+C[i]
	print("sum_C= "+str(sum_C))
	print("T_microcycle: "+ str(min_period))
	print("Sufficient Condition: "+str(sum_C/min_period))
	print("Inconclusive test")
	
	for k, v in dict_msg.items():
		print(k, v)
	print("---------")

	a = sorted(dict_msg.items(), key=lambda x: x[1]) 
	
	#calculating end2end delay---------------
	for i in range(0, len(a)):
		C_i=a[i][1][1]
		low_prio_list=set_msg_lower_prio(a[i][1][0],a)
		max_cj=max_Cj(low_prio_list)
		high_prio_list=set_msg_higher_prio(a[i][1][0],a)
		e2e_delay.append(end2end(C_i,max_cj,high_prio_list))
		print("W_"+str(a[i][0])+"="+ str(e2e_delay[i]))
		access_delay.append(-e2e_delay[i] + period[a[i][0]])
		print("Access_delay_msg_"+str(a[i][0]) +"=" + str(-e2e_delay[i] + period[a[i][0]]))
		if (-e2e_delay[i] + period[a[i][0]] >= 0):
			schd_test.append("PASS")
			print(schd_test[i])
		else:
			schd_test.append("FAIL")
			print(schd_test[i])
	
	
	create_xml(root, a, trans_delay, access_delay, e2e_delay, schd_test)
	
	
	
	
	  
if __name__ == "__main__": 
	  
# calling main function 
	main() 
