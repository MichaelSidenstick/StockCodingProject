    if '\"x\"' in message:
        # Get indexes of all needed variables for stream T
        price_index = message.index('\"p\"')
        s_index = message.index('\"s\"')
        #Get the current price
        price_current = message[(price_index+4):(s_index-1)]
        #put the price into an array
        price_array.append(price_current)
        
    if '\"v\"' in message:
        # Get indexes of all needed variables for stream AM
        opening_price_index = message.index('\"op\"')
        ticker_index = message.index('\"T\"')
        volume_index = message.index('\"v\"')
        av_index = message.index('\"av\"')
        vw_index = message.index('\"vw\"')
        #Get the ticker, volume, and opening price for the day
        ticker = message[(ticker_index + 4):(volume_index - 1)]
        volume = message[(volume_index + 5):(av_index - 2)]
        opening_price = message[(opening_price_index+5):(vw_index-1)]
