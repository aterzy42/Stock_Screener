-- Creating the 'market_indices' table with auto-incrementing 'index_id'
CREATE TABLE market_indices (
    index_id SERIAL PRIMARY KEY,           -- Automatically increments for each row
    index_ticker VARCHAR(10) NOT NULL,     -- Ticker symbol for the index (e.g., ^GSPC)
    index_name VARCHAR(255) NOT NULL,      -- Full name of the index (e.g., S&P 500)
    index_type VARCHAR(50) NOT NULL        -- Type of index (e.g., "Equity", "Bond")
);

-- Creating the 'economic_indicators' table with auto-incrementing 'indicator_id'
CREATE TABLE economic_indicators (
    indicator_id SERIAL PRIMARY KEY,       -- Automatically increments for each indicator
    indicator_name VARCHAR(255) NOT NULL,  -- Name of the economic indicator (e.g., "VIX", "Treasury Yield")
    unit_of_measure VARCHAR(50)            -- Unit of measurement (e.g., "percent", "points")
);

-- Creating the 'indicator_data' table with 'indicator_id' and 'data_date' as composite primary key
CREATE TABLE indicator_data (
    indicator_id INT NOT NULL,             -- Foreign key referencing economic_indicators
    data_date DATE NOT NULL,               -- Date of the data point
    indicator_value DECIMAL(15, 5) NOT NULL, -- Value of the economic indicator (e.g., VIX level)
    data_source VARCHAR(255) NOT NULL,     -- Source of the data (e.g., "Yahoo Finance", "FRED")
    PRIMARY KEY (indicator_id, data_date), -- Composite primary key consisting of indicator_id and data_date
    FOREIGN KEY (indicator_id) REFERENCES economic_indicators(indicator_id)  -- Foreign key relationship to economic_indicators
);

-- Creating the 'index_metrics' table with auto-incrementing 'metric_id'
CREATE TABLE index_metrics (
    metric_id SERIAL PRIMARY KEY,          -- Automatically increments for each metric
    metric_name VARCHAR(255) NOT NULL,     -- Name of the metric (e.g., "Closing Price", "Forward P/E")
    metric_unit VARCHAR(50) NOT NULL,      -- Unit of measurement (e.g., "USD", "ratio")
    metric_description TEXT               -- Optional description for the metric (e.g., "Forward Price-to-Earnings Ratio")
);

-- Creating the 'index_performance' table with composite primary key (index_id, metric_id, performance_date)
CREATE TABLE index_performance (
    index_id INT NOT NULL,                 -- Foreign key referencing market_indices
    metric_id INT NOT NULL,                -- Foreign key referencing index_metrics
    performance_date DATE NOT NULL,        -- Date for the performance data point
    metric_value DECIMAL(15, 5) NOT NULL,  -- Value of the metric on the given date
    PRIMARY KEY (index_id, metric_id, performance_date), -- Composite primary key
    FOREIGN KEY (index_id) REFERENCES market_indices(index_id),  -- Foreign key relationship to market_indices
    FOREIGN KEY (metric_id) REFERENCES index_metrics(metric_id)   -- Foreign key relationship to index_metrics
);
