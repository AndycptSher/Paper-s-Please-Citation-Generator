import argparse
import gifgen

parser = argparse.ArgumentParser(description='Generate a citation GIF.')

parser.add_argument('--output', type=str, required=True, help='Output file name for the generated GIF')
parser.add_argument('--title', type=str, default='M. O. A. CITATION', help='Title for the citation')
parser.add_argument('--reason', type=str, default='Protocol Violated.\n Attempted entry without papers.', help='Reason for the citation')
parser.add_argument('--penalty', type=str, default='WARNING ISSUED - NO PENALTY', help='Penalty for the citation')
args = parser.parse_args()

gif = gifgen.generate_citation_gif(
    title=args.title,
    penalty=args.penalty,
    reason=args.reason
)
with open(args.output, 'wb') as f:
    f.write(gif.read())
print(f'Wrote {args.output}')