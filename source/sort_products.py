import csv

products_dict = {}

with open("products.csv", "r") as csvfile:
    reader = csv.DictReader(csvfile)

    with open("products2.csv", "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow(
            ["Продукт", "Вес (г)", "Белки", "Жиры", "Углеводы", "Калории", "Категория"]
        )

        for line in reader:
            if line["Продукт"] in products_dict:
                print(f"Повтор: {line['Продукт']}")

            if "" not in [line["Вес (г)"], line["Белки"], line["Жиры"], line["Углеводы"], line["Калории"], line["Категория"]]:
                key = line["Продукт"].replace(",", "")
                products_dict[key] = [line["Вес (г)"], line["Белки"], line["Жиры"], line["Углеводы"], line["Калории"], line["Категория"]]
            elif line["Углеводы"] == "":
                products_dict[line["Продукт"]] = [line["Вес (г)"], line["Белки"], line["Жиры"], "0.0", line["Калории"], line["Категория"]]

        max = 0
        while max != 100:
            for el in products_dict:
                if len(el.split()) == max:
                    writer.writerow(
                        [el, *products_dict[el]]
                    )
            max += 1
            