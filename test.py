import os

file_path = os.path.abspath('model/popular.pkl')
print(f"Full path: {file_path}")
print(f"File exists: {os.path.exists(file_path)}")

print(os.path.exists('model/popular.pkl'))  # Should return True
print(os.path.exists('model/pt.pkl'))
print(os.path.exists('model/books.pkl'))
print(os.path.exists('model/similarity_scores.pkl'))
