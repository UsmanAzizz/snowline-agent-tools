def rata(angka):
    if not angka:
        return 0
    return sum(angka) / len(angka)
if __name__ == "__main__":
    print(rata([2, 4, 6]))
