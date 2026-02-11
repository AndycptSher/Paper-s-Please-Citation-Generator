from gifgen import generate_citation_gif

def main():
    bio = generate_citation_gif(
        title='M. O. A. CITATION',
        penalty='WARNING ISSUED - NO PENALTY',
        reason='Protocol Violated.\n Attempted entry without papers.\n Unfunny meme',
    )
    with open('sample.gif', 'wb') as f:
        f.write(bio.read())
    print('Wrote sample.gif')

if __name__ == '__main__':
    main()
