from os import getenv
index = int(getenv('JOB_COMPLETION_INDEX'))
input_data = getenv('INPUT')
year_range = range(1999, 2023, 1)
with open(input_data, 'w', encoding='utf-8') as f:
    f.write(str(year_range[index]))
    f.close()

