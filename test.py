from  backend import load_and_split

with open("ramashishh.pdf" , "rb") as file :

    data = file.read()

    chunks = load_and_split(
        file_bytes=data , 
        filename='ramashishh.pdf'
    )

    print("length of chucks " , len(chunks))

    for i , n in enumerate(chunks):
        print(n.page_content)


