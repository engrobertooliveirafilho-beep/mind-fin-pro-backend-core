from __future__ import annotations
import math
import zlib

class ComplexityEngine:
    def kolmogorov_proxy(self,data:str)->dict:
        raw=data.encode("utf-8")
        compressed=zlib.compress(raw)

        ratio=(
            len(compressed)/len(raw)
            if len(raw)>0
            else 0.0
        )

        return {
            "raw_size":len(raw),
            "compressed_size":len(compressed),
            "complexity_ratio":ratio
        }

    def lempel_ziv_complexity(self,sequence:list[int])->dict:
        s="".join(map(str,sequence))

        substrings=set()

        for i in range(len(s)):
            for j in range(i+1,len(s)+1):
                substrings.add(s[i:j])

        return {
            "length":len(s),
            "lz_complexity":len(substrings)
        }

    def mdl_score(self,model_bits:int,data_bits:int)->dict:
        total=model_bits+data_bits

        return {
            "model_bits":model_bits,
            "data_bits":data_bits,
            "mdl":total
        }
