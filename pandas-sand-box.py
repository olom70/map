#%%
import numpy as np
import pandas as pd
s = pd.Series(np.random.randn(5), index=["a", "b", "c", "e", "e"])
s
s.index
#%%
d = {"b": 1, "a": 0, "c": 3 }
pd.Series(d)
#%%
s.a
"e" in s
s.get("e")
