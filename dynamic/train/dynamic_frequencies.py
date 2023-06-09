import math
import pandas as pd
import csv

class dynamic_frequencies:
    def __init__(self, data_type: str, parsed_logs: list):
        self.data_type = data_type
        self.n = 6
        self.parsed_logs = parsed_logs
        self.unique_ngrams = []
        self.ransomware_top_calls = data_type + '-call-stats.csv'
        self.__unique_ngrams__() # fetch unique ngrams
        self.syscall_frequencies()

# obtiene n-gramas unicos de tamaño 6 y los almacena en una lista para posteriormente
# obtener sus estadísticas: qué tan comunes son entre todos los registros de cada tipo de muestra
    def __unique_ngrams__(self) -> None:
        df_calls = pd.DataFrame({'CallSeq':[],'Times':[]}) #crea dataframe
        for logs in self.parsed_logs:
            start = 0
            while start < len(logs):
                n_gram = logs[start:start+self.n]
                if n_gram not in self.unique_ngrams:
                    self.unique_ngrams.append(n_gram)
                df_calls = self.calls_count(df_calls,n_gram)
                start += 1

        df_calls = df_calls.sort_values(by=['Times'],ascending=False)
        df_calls['CallSeq'].head(150).to_csv(self.ransomware_top_calls, index=False, header=False) 

    def calls_count(self,df_calls, n_gram: list) -> None:
        n_gram = ','.join(n_gram)
        n_gram = n_gram.rstrip()
        call_empty = df_calls[df_calls['CallSeq']==n_gram]
        if call_empty.empty:
            df_calls = pd.concat([df_calls,pd.DataFrame({'CallSeq':[n_gram],'Times':1})], ignore_index=True)
        else:
            index = df_calls.index[df_calls['CallSeq'] == n_gram][0]
            df_calls.at[index,'Times'] = df_calls.at[index,'Times'] + 1
        return df_calls

    def syscall_frequencies(self) -> None:
        def sequence_stats(values: list) -> tuple:
            z_ = 1.75 # 0.90 Source: https://www.math.arizona.edu/~rsims/ma464/standardnormaltable.pdf and https://www.westga.edu/academics/research/vrc/assets/docs/confidence_intervals_notes.pdf
            n_ = len(values)
            x_ = math.floor(sum(values)/n_)
            de_ = math.floor(math.sqrt(sum([pow(x-x_,2) for x in values])/n_))
            de_n = de_/math.sqrt(n_)
            ci_l = x_ - z_ * de_n
            ci_u = x_ + z_ * de_n
            if ci_l < 0:
                ci_l = 0 # https://www.stat.berkeley.edu/~stark/SticiGui/Text/confidenceIntervals.htm
            return (math.floor(ci_l),math.floor(ci_u))

        call_final_freq = []
        with open(self.ransomware_top_calls) as list_sequences:
            top_sequences = [secuence.rstrip() for secuence in list_sequences]
        for calls in self.parsed_logs:
            calls_row = []
            for raw_sequence in top_sequences:
                sequence = raw_sequence[1:len(raw_sequence)-1].split(',')
                start = 0
                match = 0
                while start < len(calls):
                    ngram = calls[start:start+self.n]
                    if sequence == ngram:
                        match += 1
                    start += 1
                if match > 0: 
                    calls_row.append((sequence,match))
            if len(calls_row) > 0:
                call_final_freq.append(calls_row)

        end_stats = []
        for raw_sequence in top_sequences:
            sequence = raw_sequence[1:len(raw_sequence)-1].split(',')
            sequence_values = []
            for file_freq in call_final_freq:
                for seq in file_freq:
                    if sequence in seq:
                        sequence_values.append(seq[1])
                        break
            if len(sequence_values) > 0:
                ci_l, ci_u = sequence_stats(sequence_values)
                if (ci_u - ci_l) >= 5:
                    end_stats.append([sequence,(ci_l,ci_u)])

        with open('syscalls-freq-'+self.data_type+'.csv','w', newline='') as out_file:
            writer = csv.writer(out_file)
            for stat in end_stats:
                writer.writerow(stat)