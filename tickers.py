LIQUID_TICKERS = [
    # Mega / large cap tech & growth
    "AAPL","MSFT","AMZN","GOOGL","GOOG","META","NVDA","TSLA","AVGO","ADBE",
    "CRM","INTU","CSCO","ORCL","AMD","QCOM","TXN","IBM","NOW","SHOP","ADSK",
    "SNOW","PANW","CRWD","ZS","MDB","TEAM","OKTA","DDOG","NET","PLTR",

    # Financials
    "JPM","BAC","WFC","C","GS","MS","BLK","SCHW","AXP","COF","BK","TFC",
    "USB","PNC","AIG","MET","PRU","TRV","ALL","CB","MMC","SPGI","MCO",

    # Healthcare / pharma / biotech
    "UNH","JNJ","PFE","MRK","ABBV","LLY","BMY","AMGN","GILD","REGN","VRTX",
    "BIIB","ISRG","SYK","BSX","ZBH","EW","IDXX","DXCM","HOLX","ALGN",

    # Consumer staples
    "PG","KO","PEP","WMT","COST","MDLZ","KHC","K","CL","CLX","EL","STZ",
    "TAP","SYY","KR","WBA","GIS","HSY","CPB","KMB","CHD",

    # Consumer discretionary
    "HD","LOW","MCD","SBUX","NKE","TGT","DG","DLTR","ROST","TJX","MAR",
    "HLT","BKNG","RCL","CCL","NCLH","YUM","CMG","AZO","ORLY","TSCO",

    # Energy
    "XOM","CVX","COP","EOG","PXD","SLB","HAL","BKR","MPC","PSX","VLO",
    "OXY","DVN","FANG","APA","HES","MRO","CTRA",

    # Industrials
    "CAT","DE","BA","LMT","RTX","GD","NOC","HON","GE","ETN","EMR","ROK",
    "PH","ITW","MMM","DOV","CMI","PCAR","UNP","CSX","NSC","FDX","UPS",
    "DAL","UAL","LUV","AAL","RSG","WM","GWW","JCI","LEN","DHI","MAS",

    # Materials
    "LIN","APD","SHW","ECL","PPG","ALB","NEM","FCX","MLM","VMC","NUE",
    "STLD","X","CF","MOS","IFF","AVY","IP","WRK","PKG",

    # Utilities
    "NEE","DUK","SO","D","AEP","EXC","SRE","XEL","ED","EIX","PEG","WEC",
    "ES","ETR","PPL","FE","AWK","CMS",

    # Real estate
    "PLD","AMT","CCI","EQIX","DLR","O","SPG","PSA","VTR","WELL","AVB",
    "EQR","ESS","MAA","ARE","IRM","CBRE",

    # Communication services
    "DIS","NFLX","CMCSA","CHTR","T","VZ","TMUS","EA","TTWO","PARA","WBD",
    "FOX","FOXA",

    # Autos & industrial consumer
    "GM","F","STLA","HOG","PCAR","ALSN","BWA",

    # Semis (extra breadth)
    "NVDA","AMD","AVGO","QCOM","TXN","ADI","MU","NXPI","LRCX","KLAC","ASML",
    "AMAT","MCHP","ON","SWKS","QRVO","ENTG","TER","COHR",

    # Extra liquid mid/large caps (broad coverage)
    "A","AAL","AAP","ABBV","ABC","ABNB","ABT","ACGL","ACM","ACN","AEP","AES",
    "AFL","AIG","AJG","AKAM","ALB","ALL","AMAT","AME","AMGN","AMP","AMT",
    "ANET","ANSS","AON","APA","APD","APH","APTV","ARE","ATO","ATVI","AVB",
    "AWK","AXON","AZO","BALL","BAX","BBY","BDX","BEN","BIIB","BKNG","BKR",
    "BLL","BMY","BR","BRO","BSX","BWA","BXP","CAG","CAH","CARR","CB","CBOE",
    "CDAY","CDNS","CDW","CE","CEG","CF","CFG","CHD","CHRW","CI","CINF","CME",
    "CMG","CMI","CMS","CNC","CNP","COO","COP","CPRT","CPT","CRL","CSX","CTAS",
    "CTLT","CTRA","CTSH","CTVA","CVS","CZR","D","DAL","DD","DE","DFS","DGX",
    "DHI","DHR","DIS","DLR","DLTR","DOV","DOW","DPZ","DRE","DRI","DTE","DVN",
    "DXCM","EA","EBAY","ECL","ED","EFX","EIX","ELV","EMN","EMR","ENPH","EOG",
    "EQIX","EQR","EQT","ES","ESS","ETN","ETR","ETSY","EVRG","EW","EXC","EXPD",
    "EXPE","EXR","FANG","FAST","FCX","FE","FFIV","FIS","FISV","FITB","FLT",
    "FMC","FRT","FTNT","FTV","GD","GEHC","GILD","GIS","GL","GLW","GNRC","GPC",
    "GPN","GRMN","GWW","HAL","HAS","HBAN","HCA","HES","HIG","HII","HLT","HOLX",
    "HPE","HPQ","HRL","HSIC","HST","HSY","HUM","HWM","IEX","IFF","INCY","IP",
    "IPG","IQV","IR","IRM","IT","ITW","IVZ","J","JBHT","JCI","JKHY","JNPR",
    "K","KEY","KEYS","KHC","KIM","KMB","KMI","KMX","KSU","L","LDOS","LEN",
    "LH","LHX","LKQ","LNC","LNT","LUMN","LUV","LVS","LW","LYB","LYV","MCD",
    "MCHP","MCK","MCO","MDLZ","MDT","MET","MGM","MHK","MKC","MKTX","MLM",
    "MMC","MMM","MNST","MO","MOS","MPC","MPWR","MRK","MRNA","MSCI","MSI",
    "MTB","MTD","MU","NCLH","NDAQ","NEM","NKE","NOC","NTRS","NUE","NVDA",
    "NVR","NWL","NWS","NWSA","NXPI","O","ODFL","OKE","OMC","ON","ORLY","OTIS",
    "OXY","PARA","PAYX","PCAR","PEAK","PEG","PENN","PEP","PFE","PFG","PG",
    "PGR","PH","PHM","PKG","PLD","PM","PNC","PNR","PNW","PPG","PPL","PRU",
    "PSA","PWR","PXD","PYPL","QCOM","QRVO","RCL","REG","REGN","RF","RHI",
    "RJF","RL","RMD","ROK","ROL","ROP","ROST","RSG","RTX","SBAC","SBUX",
    "SCHW","SEE","SHW","SJM","SLB","SNA","SNPS","SO","SPG","SPGI","SRE",
    "STE","STLD","STT","STX","STZ","SWK","SWKS","SYF","SYK","SYY","TAP",
    "TDG","TDY","TECH","TEL","TER","TFC","TFX","TGT","TJX","TMO","TMUS",
    "TPR","TRMB","TROW","TRV","TSCO","TSN","TT","TTWO","TWTR","TXN","TXT",
    "TYL","UAL","UDR","UHS","ULTA","UNP","UPS","URI","USB","V","VFC","VLO",
    "VMC","VNO","VRSK","VRSN","VRTX","VTR","VTRS","VZ","WAB","WAT","WBA",
    "WDC","WEC","WELL","WFC","WHR","WM","WMB","WMT","WRB","WRK","WST","WTW",
    "WY","WYNN","XEL","XOM","XRAY","XYL","YUM","ZBH","ZBRA","ZION","ZTS"
]
