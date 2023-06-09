import csv

class static_detectors():
    def __init__(self, n : int, ngram : list, permission_list : list, r : int) -> None:
        self.n = n
        self.r = r
        self.selfset = []
        self.detector_set = []
        self.selfDataset = "./out/goodware/static/train/permissions.csv" # For NSA, the dataset with non-malicious samples is the "self".
        self.first_detector_set = ngram
        self.permission_list = permission_list

# obtiene los detectores de goodware utilizando un procedimiento similar al realizado
# para recuperar los detectores de ransomware
    def __generateSelfDetectors__(self) -> None:
        with open(self.selfDataset) as dataset:
            for row in dataset:
                local_ngrams = []
                permissions = row.split(",")
                start = 0
                n_local_ngrams = 0
                while n_local_ngrams < self.r:
                    n_gram = permissions[start:start+self.n]
                    clean_list = []
                    if len(n_gram) >= self.n:
                        for word in n_gram:
                            if word in self.permission_list:
                                exp = self.permission_list.index(word.rstrip())
                                clean_list.append(2**exp)
                            else:
                                clean_list.append(0)
                        n_gram = sum(clean_list)
                        if n_gram not in local_ngrams:
                            local_ngrams.append(n_gram)
                        start += 1
                    n_local_ngrams += 1
                self.selfset.append(local_ngrams)

# Elimina detectores comunes entre ambos tipos de aplicaciones
    def __generateNonSelf__(self) -> None:
        for ngram in self.first_detector_set:
            match = 0
            for chunk in self.selfset:
                if ngram in chunk:
                    match = 1
            if match == 0:
                self.detector_set.append(ngram) # si no está en ambas listas, se añade a otra lista final

# funcion que es llamada para realizar los procesos y almacenar en un archivo
    def fit(self) -> list:
        self.__generateSelfDetectors__()
        self.__generateNonSelf__()
        
        with open('./out/static-detectors.csv','w+') as saveData:
            writer = csv.writer(saveData)
            writer.writerow(self.detector_set)
        return self.detector_set
