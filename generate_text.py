import random
import string

def generate_paragraph():
    num_sentences = random.randint(3, 7)
    paragraph = ""
    for _ in range(num_sentences):
        sentence_length = random.randint(5, 15)
        sentence = ' '.join(random.choice(string.ascii_lowercase + " ") for _ in range(sentence_length)).capitalize() + '.'
        paragraph += sentence + " "
    return paragraph.strip()

def generate_text_file(filename, target_size_mb=1):
    target_size_bytes = target_size_mb * 1024 * 1024 
    current_size = 0
    
    with open(filename, 'w') as f:
        while current_size < target_size_bytes:
            paragraph = generate_paragraph() + "\n\n"
            f.write(paragraph)
            current_size = f.tell() 

    with open("test/"+ filename, 'w') as file:
        while current_size < target_size_bytes:
            paragraph = generate_paragraph() + "\n\n"
            file.write(paragraph)
            current_size = f.tell() 

generate_text_file('test_file')
