Instructions to run:

Clone repo to your computer (github tells you how, but you can also search it up if you don't know)

Then, in terminal (recommended to work in an IDE like vscode):

pip install -r requirements.txt

(if you don't have pip, you need to install python. Then, recommended: do this in a virtual python environment (venv) - search it up if you don't know how.)


Run training with a Pygame window:


python eval_neat_flappy.py --config neat-config.cfg --gens 20 --render

(this does it for 20 generations)


To visualize stats:

python visualize.py stats.pkl
