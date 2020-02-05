from main.models import Post

def sort(searchkey):
    matches = []
    titlePost = Post.title
    for i in titlePost:
        if searchkey in i:
            matches.append(i)
    return matches

