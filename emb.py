import os
from sentence_transformers import SentenceTransformer, util

def extract_text_from_file(file_path, keyword=None):
    """ Extracts text from file, optionally searching for lines after a keyword. """
    text = []
    with open(file_path, 'r') as file:
        if keyword:
            capture = False
            for line in file:
                if keyword in line:
                    capture = True
                if capture:
                    text.append(line)
        else:
            text = file.readlines()
    return ''.join(text)

def create_embedding(text, model):
    """ Creates an embedding for the provided text using a given model. """
    return model.encode(text, convert_to_tensor=True)

def main():
    # Load a pre-trained model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # File paths
    base_dir = '/.../E3_BFS'
    library_dir = '/.../library'
    target_file = os.path.join(base_dir, 'text1.txt')
    cpp_file = os.path.join(base_dir, 'tb.cpp')
    
    # Extract texts
    text1_content = extract_text_from_file(target_file, '# Error')
    cpp_content = extract_text_from_file(cpp_file)
    
    # Combine texts and create embedding
    combined_text = text1_content + cpp_content
    target_embedding = create_embedding(combined_text, model)
    
    # Compare with other files in the library
    highest_similarity = -1
    most_similar_file = None
    for file_name in os.listdir(library_dir):
        if file_name.endswith('.txt'):
            file_path = os.path.join(library_dir, file_name)
            file_text = extract_text_from_file(file_path)
            file_embedding = create_embedding(file_text, model)
            similarity = util.pytorch_cos_sim(target_embedding, file_embedding)
            
            if similarity > highest_similarity:
                highest_similarity = similarity
                most_similar_file = file_name

    
    print(f"{most_similar_file},{highest_similarity.item()}")

    #print(f"The most similar file is {most_similar_file} with a similarity of {highest_similarity.item()}.")
    #print(f"{most_similar_file}")
if __name__ == "__main__":
    main()
