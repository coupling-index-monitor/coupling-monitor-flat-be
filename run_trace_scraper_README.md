## Bash Script to run jaeger trace retriever pyhton script
The trace_scraper.py script is designed to fetch trace data from a Jaeger tracing endpoint within a specified time range, process the retrieved traces, and store them in a structured manner. It ensures that the trace data is saved in JSON files within a designated directory. The script handles pagination to retrieve all available traces, sorts them by their start time, and updates an offset file (offset.json) to keep track of the last processed trace. This allows for efficient resumption of data collection from where it left off. Additionally, the script includes logging for better visibility of its operations and handles potential errors during the data fetching and file writing processes.

### To run 
```nohup bash ./run_trace_scraper.sh > trace_scraper.log 2>&1 &```

### To view the tailing logs
```tail -f trace_scraper.log```

### To view logs 
```cat trace_scraper.log```

### To stop the script
##### Approach 1
1. run ```ps aux | grep run_trace_scraper.sh```
2. copy the PID of the process ```bash ./run_trace_scraper.sh```
3. run ```kill <Coipied PID>```

##### Approach 2
1. run ```pkill -f run_trace_scraper.sh```


