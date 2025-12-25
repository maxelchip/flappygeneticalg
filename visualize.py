import pickle
import matplotlib.pyplot as plt
import sys

def plot_stats(stats_file="stats.pkl"):
    with open(stats_file, "rb") as f:
        stats = pickle.load(f)
    gen = list(range(len(stats.get_fitness_mean())))
    mean = stats.get_fitness_mean()
    best = stats.get_fitness_stat(max)

    plt.plot(gen, mean, label="mean")
    plt.plot(gen, best, label="best")
    plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.legend()
    plt.grid(True)
    plt.title("NEAT Fitness")
    plt.show()

if __name__ == "__main__":
    plot_stats(sys.argv[1] if len(sys.argv)>1 else "stats.pkl")
