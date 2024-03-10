#Calculate freq of each text and store it in dict
#Min heap for two min freq
#Construct binary tree from Heap
#Construct code from binary tree and store in dict
#Construct encoded text
#Return binary file as output
import heapq,os
#For storing logs
import logging
#For a progress tracker
from tqdm import tqdm
#For building a GUI
import tkinter as tk
from tkinter import filedialog

class BinaryTree:
    def __init__(self,value,frequ):
        self.value=value
        self.frequ=frequ
        self.left=None
        self.right=None
    
    def __lt__(self,other):
        return self.frequ<other.frequ
    
    def __eq__(self,other):
        return self.frequ==other.frequ
    
class Huffmancode:
    def __init__(self,path):
        self.path=path
        self.__heap=[]
        self._code={}
        self.__reversecode={}
        logging.basicConfig(filename='compression_log.txt', level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        # Create a Tkinter root window
        self.root = tk.Tk()
        self.root.title("Huffman Coding Compression")
    
    
        # Create a StringVar to store the file path
        self.file_path_var = tk.StringVar()
        self.file_path_var.set(path)

        # Create a label to display the file path
        self.file_path_label = tk.Label(self.root, textvariable=self.file_path_var)
        self.file_path_label.pack(pady=10)

        # Create a button to select a file
        self.select_file_button = tk.Button(self.root, text="Select File", command=self.select_file)
        self.select_file_button.pack(pady=10)

        # Create a button to start compression and decompression
        self.compress_button = tk.Button(self.root, text="Compress/Decompress", command=self.run_compression)
        self.compress_button.pack(pady=10)

    def select_file(self):
        # Allow the user to select a file and update the file path label
        file_path = filedialog.askopenfilename(title="Select File")
        self.file_path_var.set(file_path)

    def run_compression(self):
        # Run the compression and decompression methods
        input_path = self.file_path_var.get()
        self.compression()
        self.decompress(input_path)
        
    
    def frequency_from_text(self,text):
        frequ_dict={}
        for char in text:
            if char not in frequ_dict:
                frequ_dict[char]=0
            frequ_dict[char]+=1
        return frequ_dict        
    
    def _Build_heap(self,frequency_dict):
        for key in frequency_dict:
            frequency=frequency_dict[key]
            binary_tree_node=BinaryTree(key,frequency)
            heapq.heappush(self.__heap, binary_tree_node)
    
    def _Build_Binary_Tree(self):
        while len(self.__heap)>1:
            binary_tree_node_1=heapq.heappop(self.__heap)
            binary_tree_node_2=heapq.heappop(self.__heap)
            sum_of_freq=binary_tree_node_1.frequ+binary_tree_node_2.frequ
            newnode=BinaryTree(None,sum_of_freq)
            newnode.left=binary_tree_node_1
            newnode.right=binary_tree_node_2
            heapq.heappush(self.__heap,newnode)
        return
    
    def _Build_Tree_Code_Helper(self,root,curr_bits):
        if root is None:
            return
        if root.value is not None:
            self._code[root.value]=curr_bits
            self.__reversecode[curr_bits]=root.value
            return
        
        self._Build_Tree_Code_Helper(root.left,curr_bits+'0')
        self._Build_Tree_Code_Helper(root.right,curr_bits+'1')
        
                  
    def _Build_Tree_Code(self):
         root=heapq.heappop(self.__heap)
         self._Build_Tree_Code_Helper(root,'') 
    
    def _Build_Encoded_Text(self,text):
        encoded_text=''
        for char in text:
            encoded_text+=self._code[char]
        return encoded_text 
    
    def _Build_Padded_Text(self,encoded_text):
        padding_value=8-len(encoded_text)%8
        for i in range(padding_value):
                encoded_text+='0'
        
        padded_info="{0:08b}".format(padding_value)
        #8 is for 8 bytes and b for binary format conversion
        padded_text=padded_info + encoded_text
        return padded_text
    
    def _Build_Byte_Array(self,padded_text):
        array=[]
        for i in range(0,len(padded_text),8):
           byte=padded_text[i:i+8] 
           array.append(int(byte,2))
           
        return array
    def compression(self):
        self.logger.info("Compression for your file starts.....")
        print("Compression for your file starts.....")
        filename,file_extension= os.path.splitext(self.path)
        output_path=filename+ '.bin'
        with open(self.path,'r+') as file, open(output_path,'wb') as output:
            text=file.read()
            text=text.rstrip()
            frequency_dict=self.frequency_from_text(text)
            build_heap=self._Build_heap(frequency_dict)
            self._Build_Binary_Tree()
            self._Build_Tree_Code()
            encoded_text=self._Build_Encoded_Text(text)
            padded_text=self._Build_Padded_Text(encoded_text)
            bytes_array=self._Build_Byte_Array(padded_text)
            final_bytes=bytes(bytes_array) 
            output.write(final_bytes)
        total_chars = len(text)
        with tqdm(total=total_chars, desc="Compressing", unit="char") as pbar:
            for char in text:
                encoded_text += self._code[char]
                pbar.update(1)

        print('File Compressed Successfully')
        self.logger.info('File Compressed Successfully')
        tk.messagebox.showinfo("Compression Complete", "File Compressed Successfully")
        return output_path
    
    def _Remove_Padding(self,text):
        padded_info=text[:8]
        padding_value=int(padded_info,2)
        text=text[8:]
        text=text[:-1*padding_value]
        # Negative Slicing
        return text
    
    def _Decoded_Text(self,text):
        current_bits=''
        decoded_text=''
        for char in text:
            current_bits+=char
            if current_bits in self.__reversecode:
                decoded_text+=self.__reversecode[current_bits]
                current_bits=''
        return decoded_text
                
                
    def decompress(self,input_path):
        filename,file_extension=os.path.splitext(input_path)
        output_path=filename+'_decompressed'+'.txt'
        with open(input_path,'rb') as file,open(output_path,'w')as output:
            bit_string=''
            byte=file.read(1)
            total_bits = len(bit_string)
            with tqdm(total=total_bits, desc="Decompressing", unit="bit") as pbar:
                while byte:
                    byte=ord(byte)
                    bits=bin(byte)[2:].rjust(8,'0')
                    bit_string+=bits
                    pbar.update(8)
                    byte=file.read(1) 
                    
                
            text_after_removing_padding=self._Remove_Padding(bit_string)
            actual_text=self._Decoded_Text(text_after_removing_padding)
            output.write(actual_text)
            self.logger.info('Decompression completed successfully.')   
            tk.messagebox.showinfo("Decompression Complete", "Decompression completed successfully.") 
    
    def start_gui(self):
        # Start the Tkinter main loop
        self.root.mainloop()
if __name__ == "__main__":
    path=input("Enter the path of your file which you want to compress\n")
    h=Huffmancode(path)
    h.start_gui()
    compressed_file=h.compression()
    h.decompress(compressed_file)

    