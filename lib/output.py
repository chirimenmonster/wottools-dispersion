
import io
import csv
import json

from lib.stats import VehicleStatsCollection


def outputValues(records, shows=None, headers=None, option=None):
    if isinstance(shows, str):
        shows = shows.split(',')
    if isinstance(headers, str):
        headers = headers.split(',')
    if option and option.output_csv:
        result = getOutputCsv(records, shows, headers, option)
    elif option and option.output_json:
        result = getOutputJson(records, shows, headers, option)
    else:
        result = getOutputText(records, shows, headers, option)
    print(result, end='')


def getOutputText(records, shows=None, headers=None, option=None):
    if len(records) == 0:
        return
    if headers is None:
        headers = shows
    headers = { k:h for k,h in zip(shows, headers) }
    rowlen = { k:max([ len(r[k].getFormattedString()) for r in records ]) for k in shows }
    result = []
    if option and not option.suppress_header:
        rowlen = { k:max(rowlen[k], len(headers[k])) for k in shows }
        result.append('  '.join([ headers[k].ljust(rowlen[k]) for k in shows ]))
    for r in records:
        result.append('  '.join([ r[k].getFormattedString(width=rowlen[k]) for k in shows ]))
    result = '\n'.join(result)
    return result


def getOutputJson(records, shows=None, headers=None, option=None):
    records = [ r.asDict() for r in records ]
    result = json.dumps(records, ensure_ascii=False, indent=2)
    return result


def getOutputCsv(records, shows=None, headers=None, option=None):
    if headers is None:
        headers = shows
    if option and option.suppress_header:
        headers = None
    output = io.StringIO(newline='')
    writer = csv.writer(output, dialect='excel', lineterminator='\n')
    if headers:
        writer.writerow(headers)
    if isinstance(records, VehicleStatsCollection):
        for r in records:
            writer.writerow(list(map(lambda k: r[k].orig, shows)))
    elif isinstance(records, list):
        for r in records:
            writer.writerow(list(map(lambda k: r[k], shows)))
    elif isinstance(records, dict):
        for k,v in records.items():
            writer.writerow([k, v])        
    else:
        raise NotImplementedError
    result = output.getvalue()
    return result
