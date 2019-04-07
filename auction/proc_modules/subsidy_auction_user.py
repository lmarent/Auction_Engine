
int lastBidGenerated = 0;
int domainId = 0;
ipap_field_container g_ipap_fields;

class SubsidyAuctionUser(Module):

    def __init__(self, module_name: str, module_file: str, module_handle, config_group: str):
        super(SubsidyAuctionUser, self).__init__(module_name, module_file, module_handle, config_group)
        self.config_param_list = {}
        self.proc_module = ProcModule()
        self.domain = 0
        self.logger = log().get_logger()

    def init_module(self, config_params: dict):
        self.config_param_list = config_params
        self.domain = config_params['domainid']

    def check_parameters(self, request_params):
        required_fields = set()
        required_fields.add(self.proc_module.field_def_manager.get_field("quantity"))
        required_fields.add(self.proc_module.field_def_manager.get_field("unitbudget"))
        required_fields.add(self.proc_module.field_def_manager.get_field("maxvalue"))

        for field in required_fields:
            if field['key'] not in request_params:
                raise ValueError("basic module: ending check - it does not pass the check, \
                                 field not included {0}".format(field['key']))


    def create_bidding_object(self, auction_key: str, quantity: float, unit_budget: float,
                              unit_price: float, start: datetime, stop: datetime) -> BiddingObject:

        self.logger.debug("starting create bidding object")
        if unit_budget < unit_price:
            unit_price = unit_budget

        # build the elements of the bidding object
        elements = dict()
        config_elements = dict()
        record_id = "record_1"
        self.proc_module.insert_string_field("recordid", record_id, config_elements)
        self.proc_module.insert_float_field("quantity", quantity, config_elements)
        self.proc_module.insert_double_field("unitprice", unit_price, config_elements)
        elements[record_id] = config_elements

        # build the options (time intervals)
        options = dict()
        option_id = 'option_1'
        config_options = dict()
        self.proc_module.insert_datetime_field("start", start, config_options)
        self.proc_module.insert_datetime_field("stop", stop, config_options)
        options[option_id] = config_options

        bidding_object_id = self.proc_module.get_bidding_object_id()
        bidding_object_key = str(self.domain) + '.' + bidding_object_id
        bidding_object = BiddingObject(auction_key, bidding_object_key,
                                       AuctioningObjectType.BID, elements, options)

        self.logger.debug("ending create bidding object")
        return bidding_object


    def destroy_module(self):
        pass


float getSubsidy(auction::configParam_t * params )
{

    # ifdef DEBUG
    cout << "Starting getSubsidy" << endl;
    # endif

    float subsidy = 0;
    int numparams = 0;

    while (params[0].name != NULL) {
        # in all the application we establish the rates and
        # burst parameters in bytes

        if (!strcmp(params[0].name, "subsidy")) {
            subsidy = (float) parseFloat( params[0].value );
            numparams++;
        }
        params++;
    }

    if (numparams == 0)
        throw auction::ProcError(AUM_PROC_PARAMETER_ERROR,
                           "subsidy auction init module - not enought parameters");

    if (subsidy <= 0)
        throw auction::ProcError(AUM_FIELD_NOT_FOUND_ERROR,
                           "subsidy auction init module - The given subsidy parameter is incorrect");

    # ifdef DEBUG
    cout << "Ending getSubsidy - Subsidy:" << subsidy << endl;
    # endif

    return subsidy;

}

double getDiscriminatingBid(auction::configParam_t * params )
{

    # ifdef DEBUG
    cout << "Starting get Discriminating Bid" << endl;
    # endif

    double discriminatingBid = 0;
    int numparams = 0;

    while (params[0].name != NULL) {
        # in all the application we establish the rates and
        # burst parameters in bytes

        if (!strcmp(params[0].name, "maxvalue01")) {
            discriminatingBid = (float) parseDouble( params[0].value );
            numparams++;
        }
        params++;
    }

    if (numparams == 0)
        throw auction::ProcError(AUM_PROC_PARAMETER_ERROR,
                           "subsidy auction init module - not enought parameters");

    if (discriminatingBid <= 0)
        throw auction::ProcError(AUM_FIELD_NOT_FOUND_ERROR,
                           "subsidy auction init module - The given discriminating bid parameter (maxvalue01) is incorrect");

    # ifdef DEBUG
    cout << "Ending Discriminating Bid:" << discriminatingBid << endl;
    # endif

    return discriminatingBid;

}

    def execute(self, request_params: Dict[str, FieldValue], auction_key: str,
                start: datetime, stop: datetime, bids: dict) -> list:
        return []


void auction::execute_user(auction::fieldDefList_t * fieldDefs, auction::fieldValList_t * fieldVals,
                           auction::fieldList_t * requestparams, auction::auctioningObjectDB_t * auctions,
                           time_t start, time_t stop, auction::auctioningObjectDB_t ** biddata )
{

    # ifdef DEBUG
    fprintf(stdout, "subsidy auction module: start execute with # %d of auctions \n", (int)
    auctions->size() );
    # endif

    auction::fieldDefItem_t fieldItem;
    double budget, valuation;
    double budgetByAuction, valuationByAuction, maxGrpValation;
    float quantity, subsidy;
    double unitPrice;

    int check_ret = check(fieldDefs, requestparams);

    if ((check_ret > 0) & & (auctions->size() > 0) ){

        # Get the total money and budget and divide them by the number of auctions
        fieldItem = auction::IpApMessageParser::findField(fieldDefs, 0, IPAP_FT_UNITBUDGET);
        budget = getDoubleField(requestparams, fieldItem.name);

        fieldItem = auction::IpApMessageParser::findField(fieldDefs, 0, IPAP_FT_MAXUNITVALUATION);
        valuation = getDoubleField(requestparams, fieldItem.name);

        fieldItem = auction::IpApMessageParser::findField(fieldDefs, 0, IPAP_FT_QUANTITY);
        quantity = getFloatField(requestparams, fieldItem.name);

        budgetByAuction = budget / (int) auctions->size();
        valuationByAuction = valuation / (int) auctions->size();

        unitPrice = valuationByAuction;
        if (budgetByAuction < valuationByAuction)
        {
            unitPrice = budgetByAuction;
        }


        auctioningObjectDBIter_t auctIter;
        for (auctIter = auctions->begin(); auctIter != auctions->end(); ++auctIter)
        {

            Auction * auctionTmp = dynamic_cast < Auction * > (*auctIter);

            subsidy = getSubsidy(ConfigManager::getParamList(auctionTmp->getAction()->conf ));

            maxGrpValation = getDiscriminatingBid(ConfigManager::getParamList(auctionTmp->getAction()->conf ));

            # Set the optimal bid.
            if (unitPrice < (maxGrpValation * subsidy))
            {
                if (unitPrice > maxGrpValation)
                {
                    unitPrice = maxGrpValation;
                }
            }

            auction::BiddingObject * bid = createBid(fieldDefs, fieldVals, auctionTmp, quantity,
                                                     unitPrice, start, stop);
            (*biddata)->push_back(bid);
        }

        # ifdef DEBUG
        fprintf(stdout, "subsidy auction module: in the middle 2 \n");
        # endif

    } else {
        throw ProcError("A required field was not provided");
    }

    # ifdef DEBUG
    fprintf(stdout, "subsidy auction module: end execute \n");
    # endif

}

void
auction::destroy(auction::configParam_t * params )
{
    # ifdef DEBUG
    fprintf(stdout, "subsidy auction module: start destroy \n");
    # endif

    g_ipap_fields.clear();

    # ifdef DEBUG
    fprintf(stdout, "subsidy auction module: end destroy \n");
    # endif
}

    def reset(self):
        print('reset')


const char * auction::getModuleInfo(int i )
{
    # ifdef DEBUG
    fprintf(stdout, "subsidy auction module: start getModuleInfo \n");
    # endif

    / *fprintf(stderr, "count : getModuleInfo(%d)\n", i); * /

    switch(i)
    {
        case
    auction::I_MODNAME:
    return "Subsidy Auction User procedure";
    case
    auction::I_ID:
    return "subsidyauctionuser";
    case
    auction::I_VERSION:
    return "0.1";
    case
    auction::I_CREATED:
    return "2015/12/30";
    case
    auction::I_MODIFIED:
    return "2015/12/30";
    case
    auction::I_BRIEF:
    return "Bid process that gives subsidies to a target user group";
    case
    auction::I_VERBOSE:
    return "The auction just put the budget and unit price given as parameters";
    case
    auction::I_HTMLDOCS:
    return "http://www.uniandes.edu.co/... ";
    case
    auction::I_PARAMS:
    return "IPAP_FT_QUANTITY (requested quantiry), IPAP_FT_UNITBUDGET (Total Budget by unit), IPAP_FT_MAXUNITVALUATION (own valuation), IPAP_FT_MAXUNITVALUATION01 (Discriminating Bid), IPAP_FT_SUBSIDY (Subsidy), IPAP_FT_STARTSECONDS, IPAP_FT_ENDSECONDS";
    case
    auction::I_RESULTS:
    return "The user's bid";
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
    fprintf(stdout, "subsidy auction user module: end getModuleInfo \n");
    # endif
}

