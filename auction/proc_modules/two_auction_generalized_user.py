
int lastBidGenerated = 0;
int domainId = 0;
ipap_field_container g_ipap_fields;

void auction::initModule( auction::configParam_t *params )
{

    # ifdef DEBUG
    fprintf(stdout, "two auction generalized module: start init module \n");
    # endif

    # Randomly assign the domain Id.
    uint32_t nbr;
    int ret = RAND_bytes((unsigned char *) & nbr, sizeof(uint32_t));
    assert (ret == 1);
    domainId = nbr;

    # Bring fields defined for ipap_messages;
    g_ipap_fields.clear();
    g_ipap_fields.initialize_forward();
    g_ipap_fields.initialize_reverse();


    # ifdef DEBUG
    fprintf( stdout, "two auction generalized module: end init module \n");
    # endif

}

void auction::destroyModule(auction::configParam_t * params )
{
    # ifdef DEBUG
    fprintf(stdout, "two auction generalized module: start destroy module \n");
    # endif

    # Return the lastBid generated.

    # ifdef DEBUG
    fprintf(stdout, "two auction generalized module: end destroy module \n");
    # endif

}

# Return 1 if Ok, 0 otherwise.
int
check(auction::fieldDefList_t * fieldDefs, auction::fieldList_t * requestparams)
{

    # ifdef DEBUG
    cout << "two auction generalized module: starting check" << endl;;
    # endif

    set < ipap_field_key > requiredFields;
    requiredFields.insert(ipap_field_key(0, IPAP_FT_QUANTITY));
    requiredFields.insert(ipap_field_key(0, IPAP_FT_UNITBUDGET));
    requiredFields.insert(ipap_field_key(0, IPAP_FT_MAXUNITVALUATION));

    set < ipap_field_key >::iterator iter;

    for (iter = requiredFields.begin(); iter != requiredFields.end(); ++iter)
    {
        auction:: fieldDefItem_t fieldItem = auction::IpApMessageParser::findField(fieldDefs, iter->get_eno(), iter->get_ftype());
        if ((fieldItem.name).empty()){
            # ifdef DEBUG
            fprintf( stdout, "two auction generalized module: ending check - it does not pass the check, field not parametrized %d.%d \n",
                    iter->get_eno(), iter->get_ftype());
            # endif
            return 0;
        }
        else {
            if (auction::IpApMessageParser::isFieldIncluded(requestparams, fieldItem.name) == false){
                # ifdef DEBUG
                fprintf( stdout, "two auction generalized module: ending check - it does not pass the check, field not included %d.%d \n",
                        iter->get_eno(), iter->get_ftype());
                # endif
                return 0;
            }
        }
    }

    # ifdef DEBUG
    fprintf(stdout, "two auction generalized module: ending check - it pass the check \n");
    # endif

    return 1;
}




auction::BiddingObject * createBid(auction::fieldDefList_t * fieldDefs, auction::fieldValList_t * fieldVals,
                                   auction::Auction * auct, float quantity, double unitbudget, double unitprice, \
                                   time_t start, time_t stop )
{
    uint64_t timeUint64;
    auction::BiddingObject * bid = NULL;

    auction::elementList_t elements;
    auction::optionList_t options;

    # Insert elements that belong to the bid

    auction::fieldList_t elementFields;

    # Insert Record Id.
    string recordId = "Unique";
    fillField(fieldDefs, fieldVals, 0, IPAP_FT_IDRECORD, recordId, & elementFields);

    # Insert quantity ipap_field
    fQuantity = g_ipap_fields.get_field(0, IPAP_FT_QUANTITY);
    ipap_value_field fVQuantity = fQuantity.get_ipap_value_field(quantity);
    string squantity = fQuantity.writeValue(fVQuantity);
    fillField(fieldDefs, fieldVals, 0, IPAP_FT_QUANTITY, squantity, & elementFields);

    if (unitprice > unitbudget){
        unitprice = unitbudget;
    }

    # Insert unit price ipap_field
    fUnitPrice = g_ipap_fields.get_field(0, IPAP_FT_UNITVALUE);
    ipap_value_field fVUnitPrice = fUnitPrice.get_ipap_value_field(unitprice);
    string sunitprice = fUnitPrice.writeValue(fVUnitPrice);
    fillField(fieldDefs, fieldVals, 0, IPAP_FT_UNITVALUE, sunitprice, & elementFields);

    elements[recordId] = elementFields;

    # Insert options that belong to the bid.
    string optionId = "Unique";
    auction::fieldList_t
    optionFields;

    # Insert start ipap_field
    fStart = g_ipap_fields.get_field(0, IPAP_FT_STARTSECONDS);
    timeUint64 = *reinterpret_cast < uint64_t * > (& start);
    ipap_value_field fVStart = fStart.get_ipap_value_field(timeUint64);
    string sstart = fStart.writeValue(fVStart);
    fillField(fieldDefs, fieldVals, 0, IPAP_FT_STARTSECONDS, sstart, & optionFields);

    # Insert stop ipap_field
    fStop = g_ipap_fields.get_field(0, IPAP_FT_ENDSECONDS);
    timeUint64 = *reinterpret_cast < uint64_t * > (& stop);
    ipap_value_field fVStop = fStop.get_ipap_value_field(timeUint64);
    string sstop = fStop.writeValue(fVStop);
    fillField(fieldDefs, fieldVals, 0, IPAP_FT_ENDSECONDS, sstop, & optionFields);

    options.push_back(pair < string, auction::fieldList_t > (optionId, optionFields));

    # Bid Set and name
    string bidSet = intToString(domainId);
    uint32_t lid = getId();
    string bidName = uint32ToString(lid);

    bid = new auction::BiddingObject(auct->getSet(), auct->getName(),
                                                 bidSet, bidName, IPAP_BID, elements, options);

    return bid;

}

void auction::execute(auction::fieldDefList_t * fieldDefs, auction::fieldValList_t * fieldVals,
                      auction::configParam_t * params, string aset, string aname, time_t start, time_t stop,
                      auction::auctioningObjectDB_t * bids, auction::auctioningObjectDB_t ** allocationdata )
{
    # NOTHING TO DO.
}

void auction::execute_user(auction::fieldDefList_t * fieldDefs, auction::fieldValList_t * fieldVals,
                           auction::fieldList_t * requestparams, auction::auctioningObjectDB_t * auctions,
                           time_t start, time_t stop, auction::auctioningObjectDB_t ** biddata )
{

    # ifdef DEBUG
    fprintf(stdout, "two auction generalized module: start execute with # %d of auctions \n", (int)
    auctions->size() );
    # endif

    auction::fieldDefItem_t fieldItem;
    double budget, valuation;
    double budgetByAuction, valuationByAuction;
    float quantity;

    int check_ret = check(fieldDefs, requestparams);

    if ((check_ret > 0) & & (auctions->size() > 0) ){

        # Get the total money and budget and divide them by the number of auctions
        fieldItem = auction::IpApMessageParser::findField(fieldDefs, 0, IPAP_FT_UNITBUDGET);
        budget = getDoubleField(requestparams, fieldItem.name);

        fieldItem = auction::IpApMessageParser::findField(fieldDefs, 0, IPAP_FT_MAXUNITVALUATION);
        valuation = getDoubleField(requestparams, fieldItem.name);

        fieldItem = auction::IpApMessageParser::findField(fieldDefs, 0, IPAP_FT_QUANTITY);
        quantity = getFloatField(requestparams, fieldItem.name);

        # start and stop time come from the auction, because they are replaced by the interval definition.
        auctioningObjectDBIter_t firstAuct = auctions->begin();

        budgetByAuction = budget;;
        valuationByAuction = valuation;

        auctioningObjectDBIter_t auctIter;
        for (auctIter = auctions->begin(); auctIter != auctions->end(); ++auctIter)
        {
            auction:: Auction * auction = dynamic_cast < auction::Auction * > (*auctIter);

            auction::BiddingObject * bid = createBid(fieldDefs, fieldVals, auction, quantity,
                                                 budgetByAuction, valuationByAuction,
                                                 start, stop);
            (*biddata)->push_back(bid);
        }

        # ifdef DEBUG
        fprintf(stdout, "two auction generalized module: in the middle 2 \n");
        # endif

    } else {
        throw ProcError("A required field was not provided");
    }

    # ifdef DEBUG
    fprintf(stdout, "two auction generalized module: end execute \n");
    # endif

}

void auction::destroy(auction::configParam_t * params )
{
    # ifdef DEBUG
    fprintf(stdout, "two auction generalized module: start destroy \n");
    # endif

    g_ipap_fields.clear();

    # ifdef DEBUG
    fprintf(stdout, "two auction generalized module: end destroy \n");
    # endif
}

void auction::reset(auction::configParam_t * params )
{
    # ifdef DEBUG
    cout << "two auction generalized module: start reset module" << endl;
    # endif

    int numparams = 0;

    while (params[0].name != NULL) {
    # in all the application we receive the next allocation id to create

        if (caseInsensitiveStringCompare(params[0].name, "domainid")) {
            domainId = parseUInt32( params[0].value );
            numparams++;
            # ifdef DEBUG
            cout << "two auction generalized module: domainId:" << domainId << endl;
            # endif
        }
        params++;
    }

    if (numparams != MOD_REINIT_REQUIRED_PARAMS)
        throw
        ProcError("two auction generalized init module - not enought parameters");

    # ifdef DEBUG
    cout << "two auction generalized module: end reset module" << endl;
    # endif


    # ifdef DEBUG
    fprintf(stdout, "two auction generalized module: end reset \n");
    # endif
}

const char * auction::getModuleInfo(int i )
{
    # ifdef DEBUG
    fprintf(stdout, "two auction generalized module: start getModuleInfo \n");
    # endif

    / *fprintf(stderr, "count : getModuleInfo(%d)\n", i); * /

    switch(i)
    {
        case
    auction::I_MODNAME:
    return "Two Auction Generalized User procedure";
    case
    auction::I_ID:
    return "twoauctiongeneralizeduser";
    case
    auction::I_VERSION:
    return "0.1";
    case
    auction::I_CREATED:
    return "2016/03/08";
    case
    auction::I_MODIFIED:
    return "2016/03/08";
    case
    auction::I_BRIEF:
    return "Bidding process for the generalized two auction mechanism";
    case
    auction::I_VERBOSE:
    return "The auction just choose the minimum between the budget and unit price given as parameters";
    case
    auction::I_HTMLDOCS:
    return "http://www.uniandes.edu.co/... ";
    case
    auction::I_PARAMS:
    return "IPAP_FT_QUANTITY, IPAP_FT_UNITBUDGET, IPAP_FT_MAXUNITVALUATION, IPAP_FT_STARTSECONDS, IPAP_FT_ENDSECONDS";
    case
    auction::I_RESULTS:
    return "A bidding for the request";
    case
    auction::I_AUTHOR:
    return "Andres Marentes";
    case
    auction::I_AFFILI:
    return "Universidad de los Andes, Colombia";
    case
    auction::I_EMAIL:
    return "la.marentes455@uniandes.edu.co";
    case
    auction::I_HOMEPAGE:
    return "http://homepage";
    default:
    return NULL;
    }

    # ifdef DEBUG
    fprintf(stdout, "two auction generalized user module: end getModuleInfo \n");
    # endif
}

char * auction::getErrorMsg(int code )
{
    # ifdef DEBUG
    fprintf(stdout, "two auction generalized user module: start getErrorMsg \n");
    # endif

    return NULL;

    # ifdef DEBUG
    fprintf(stdout, "two auction generalized user module: end getErrorMsg \n");
    # endif
}