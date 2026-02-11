from gifgen import generate_citation_gif

def main():
    bio = generate_citation_gif('TEST SUBJECT', '111-222', 'Attempted entry without papers', 'APPROVED')
    with open('sample.gif', 'wb') as f:
        f.write(bio.read())
    print('Wrote sample.gif')

if __name__ == '__main__':
    main()
