import requests
import datetime
import csv 
from BeautifulSoup import BeautifulSoup
import os

def get_temp_percip(yr, mo, dy):
    
    url = 'https://www.wunderground.com/history/airport/KJFK/{y}/{m}/{d}/DailyHistory.html?MR=1'.format(y=yr, m=mo, d=dy)
    response = requests.get(url)
    html = response.content
    soup = BeautifulSoup(html)
    table = soup.find('table', attrs={'id': 'historyTable'})
    rows = []
    for row in table.findAll('tr')[1:]:
        cells = []
        for cell in row.findAll('td'):
            text = cell.text.replace('&nbsp', '')
            cells.append(text)
        rows.append(cells)  
    for row in rows:
        #print row
        if row[0] == u'Max Temperature':
            max_temp = row[1]
        if row[0] == u'Mean Temperature':
            mean_temp = row[1]
        if row[0] == u'Min Temperature':
            min_temp = row[1]
        if row[0] == 'Precipitation' and len(row) > 2:
            percip = row[1]
            if percip == 'T;in':
                percip = '0.1;in'
    return int(max_temp.replace(';&deg;F','')), float(percip.replace(';in','')), int(mean_temp.replace(';&deg;F','')), int(min_temp.replace(';&deg;F',''))
        
def nice_weather(yr, mo, dy):
    max_temp, percip, mean_temp, min_temp = get_temp_percip(yr, mo, dy)
    if max_temp > 60 and percip < 1:
        return 'Nice', max_temp, percip, mean_temp, min_temp
    else:
        return 'Not Nice', max_temp, percip, mean_temp, min_temp

def write_csv(out_file, data_to_write, header=None):
    row_cnt = 0
    with open(out_file, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        # write the header of your output file so the next person reading it knows what the fields are
        if header:
            writer.writerow(header)
        # loop through your data and write out
        for row in data_to_write:
            writer.writerow(row)  # this writes the rows to the csv file row needs to be a list
            row_cnt += 1
    return str(row_cnt) + " rows were written to " + str(out_file)


if __name__ == '__main__':
    weather = list()
    header = ['date', 'status', 'max temp', 'mean temp', 'min temp', 'percip', 'dow']
    wkdy = {7:'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday'}

    start = datetime.datetime(2003, 12, 31, 0, 0, 0, 0)
    delta = datetime.timedelta(days = 1)
    while start < datetime.datetime.now():
        start = start + delta
        status, temp, percip, mean_temp, min_temp = nice_weather(start.year, start.month, start.day)
        weather.append([start.strftime('%Y-%m-%d'), status, temp, mean_temp, min_temp, percip, wkdy[start.isoweekday()]])
        print '{} ({}) had {} weather'.format(start.strftime('%Y-%m-%d'),wkdy[start.isoweekday()], status)

    write_csv('historical_weather.csv', weather, header)
    os.startfile('historical_weather.csv')
