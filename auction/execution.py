import subprocess
import time
import signal
import pathlib
import yaml


def update_configuration_file(file_name: str, config_group: str, option: str, value: str):
    """

    :param file_name:
    :param config_group:
    :param option:
    :param value:
    :return:
    """
    base_dir = pathlib.Path(__file__).parent.parent
    file_name = base_dir / 'config' / file_name
    ok = False
    with open(file_name) as f:
        file = yaml.load(f)
        try:
            file[config_group][option] = value
            ok = True
        except:
            raise ValueError("some problem with the config group and option")

    if ok:
        with open(file_name, "w") as f:
            yaml.dump(file, f, default_flow_style=False)


if __name__ == '__main__':

    configurations = []
    # aggregate 1
    # configurations.append({'domain_server': 114, 'domain_client': 24,
    #                       'auction_file': 'auction_basic.xml', 'request_file': 'aggregate_basic.xml'})

    # configurations.append({'domain_server': 119, 'domain_client': 29, 'auction_file': 'auction_perfect_information.xml',
    #                        'request_file': 'aggregate_perfect_information.xml'})

    #configurations.append({'domain_server': 116, 'domain_client': 26, 'auction_file': 'auction_psp.xml',
    #                       'request_file': 'aggregate_psp.xml'})

    #configurations.append({'domain_server': 117, 'domain_client': 27, 'auction_file': 'auction_subsidy.xml',
    #                       'request_file': 'aggregate_subsidy.xml'})

    configurations.append(
        {'domain_server': 138, 'domain_client': 48, 'auction_file': 'auction_two_auction_generalized.xml',
         'request_file': 'aggregate_two_auction_generalized.xml'})

    # aggregate 2
    # configurations.append({'domain_server': 106, 'domain_client': 16, 'auction_file': 'auction_basic.xml', 'request_file': 'aggregate_basic.xml'})
    # configurations.append({'domain_server': 107, 'domain_client': 17, 'auction_file': 'auction_perfect_information.xml', 'request_file': 'aggregate_perfect_information.xml'})
    # configurations.append({'domain_server': 108, 'domain_client': 18, 'auction_file': 'auction_psp.xml', 'request_file': 'aggregate_psp.xml'})
    # configurations.append({'domain_server': 109, 'domain_client': 19, 'auction_file': 'auction_subsidy.xml', 'request_file': 'aggregate_subsidy.xml'})
    # configurations.append({'domain_server': 110, 'domain_client': 20, 'auction_file': 'auction_two_auction_generalized.xml', 'request_file': 'aggregate_two_auction_generalized.xml'})
    #
    # # aggregate 3
    # configurations.append({'domain_server': 111, 'domain_client': 21, 'auction_file': 'auction_basic.xml', 'request_file': 'aggregate_basic.xml'})
    # configurations.append({'domain_server': 112, 'domain_client': 22, 'auction_file': 'auction_perfect_information.xml', 'request_file': 'aggregate_perfect_information.xml'})
    # configurations.append({'domain_server': 113, 'domain_client': 23, 'auction_file': 'auction_psp.xml', 'request_file': 'aggregate_psp.xml'})
    # configurations.append({'domain_server': 114, 'domain_client': 24, 'auction_file': 'auction_subsidy.xml', 'request_file': 'aggregate_subsidy.xml'})
    # configurations.append({'domain_server': 115, 'domain_client': 25, 'auction_file': 'auction_two_auction_generalized.xml', 'request_file': 'aggregate_two_auction_generalized.xml'})
    #
    # # aggregate 4
    # configurations.append({'domain_server': 116, 'domain_client': 26, 'auction_file': 'auction_basic.xml', 'request_file': 'aggregate_basic.xml'})
    # configurations.append({'domain_server': 117, 'domain_client': 27, 'auction_file': 'auction_perfect_information.xml', 'request_file': 'aggregate_perfect_information.xml'})
    # configurations.append({'domain_server': 118, 'domain_client': 28, 'auction_file': 'auction_psp.xml', 'request_file': 'aggregate_psp.xml'})
    # configurations.append({'domain_server': 119, 'domain_client': 29, 'auction_file': 'auction_subsidy.xml', 'request_file': 'aggregate_subsidy.xml'})
    # configurations.append({'domain_server': 120, 'domain_client': 30, 'auction_file': 'auction_two_auction_generalized.xml', 'request_file': 'aggregate_two_auction_generalized.xml'})
    #
    # # aggregate 5
    # configurations.append({'domain_server': 121, 'domain_client': 31, 'auction_file': 'auction_basic.xml', 'request_file': 'aggregate_basic.xml'})
    # configurations.append({'domain_server': 122, 'domain_client': 32, 'auction_file': 'auction_perfect_information.xml', 'request_file': 'aggregate_perfect_information.xml'})
    # configurations.append({'domain_server': 123, 'domain_client': 33, 'auction_file': 'auction_psp.xml', 'request_file': 'aggregate_psp.xml'})
    # configurations.append({'domain_server': 124, 'domain_client': 34, 'auction_file': 'auction_subsidy.xml', 'request_file': 'aggregate_subsidy.xml'})
    # configurations.append({'domain_server': 125, 'domain_client': 35, 'auction_file': 'auction_two_auction_generalized.xml', 'request_file': 'aggregate_two_auction_generalized.xml'})
    #
    # # aggregate 6
    # configurations.append({'domain_server': 126, 'domain_client': 36, 'auction_file': 'auction_basic.xml', 'request_file': 'aggregate_basic.xml'})
    # configurations.append({'domain_server': 127, 'domain_client': 37, 'auction_file': 'auction_perfect_information.xml', 'request_file': 'aggregate_perfect_information.xml'})
    # configurations.append({'domain_server': 128, 'domain_client': 38, 'auction_file': 'auction_psp.xml', 'request_file': 'aggregate_psp.xml'})
    # configurations.append({'domain_server': 129, 'domain_client': 39, 'auction_file': 'auction_subsidy.xml', 'request_file': 'aggregate_subsidy.xml'})
    # configurations.append({'domain_server': 130, 'domain_client': 40, 'auction_file': 'auction_two_auction_generalized.xml', 'request_file': 'aggregate_two_auction_generalized.xml'})
    #
    # # aggregate 7
    # configurations.append({'domain_server': 131, 'domain_client': 41, 'auction_file': 'auction_basic.xml', 'request_file': 'aggregate_basic.xml'})
    # configurations.append({'domain_server': 132, 'domain_client': 42, 'auction_file': 'auction_perfect_information.xml', 'request_file': 'aggregate_perfect_information.xml'})
    # configurations.append({'domain_server': 133, 'domain_client': 43, 'auction_file': 'auction_psp.xml', 'request_file': 'aggregate_psp.xml'})
    # configurations.append({'domain_server': 134, 'domain_client': 44, 'auction_file': 'auction_subsidy.xml', 'request_file': 'aggregate_subsidy.xml'})
    # configurations.append({'domain_server': 135, 'domain_client': 45, 'auction_file': 'auction_two_auction_generalized.xml', 'request_file': 'aggregate_two_auction_generalized.xml'})
    #
    # # aggregate 8
    # configurations.append({'domain_server': 136, 'domain_client': 46, 'auction_file': 'auction_basic.xml', 'request_file': 'aggregate_basic.xml'})
    # configurations.append({'domain_server': 137, 'domain_client': 47, 'auction_file': 'auction_perfect_information.xml', 'request_file': 'aggregate_perfect_information.xml'})
    # configurations.append({'domain_server': 138, 'domain_client': 48, 'auction_file': 'auction_psp.xml', 'request_file': 'aggregate_psp.xml'})
    # configurations.append({'domain_server': 139, 'domain_client': 49, 'auction_file': 'auction_subsidy.xml', 'request_file': 'aggregate_subsidy.xml'})
    # configurations.append({'domain_server': 140, 'domain_client': 50, 'auction_file': 'auction_two_auction_generalized.xml', 'request_file': 'aggregate_two_auction_generalized.xml'})
    #
    # # aggregate 9
    # configurations.append({'domain_server': 141, 'domain_client': 51, 'auction_file': 'auction_basic.xml', 'request_file': 'aggregate_basic.xml'})
    # configurations.append({'domain_server': 142, 'domain_client': 52, 'auction_file': 'auction_perfect_information.xml', 'request_file': 'aggregate_perfect_information.xml'})
    # configurations.append({'domain_server': 143, 'domain_client': 53, 'auction_file': 'auction_psp.xml', 'request_file': 'aggregate_psp.xml'})
    # configurations.append({'domain_server': 144, 'domain_client': 54, 'auction_file': 'auction_subsidy.xml', 'request_file': 'aggregate_subsidy.xml'})
    # configurations.append({'domain_server': 145, 'domain_client': 55, 'auction_file': 'auction_two_auction_generalized.xml', 'request_file': 'aggregate_two_auction_generalized.xml'})
    #
    # # aggregate 10
    # configurations.append({'domain_server': 146, 'domain_client': 56, 'auction_file': 'auction_basic.xml', 'request_file': 'aggregate_basic.xml'})
    # configurations.append({'domain_server': 147, 'domain_client': 57, 'auction_file': 'auction_perfect_information.xml', 'request_file': 'aggregate_perfect_information.xml'})
    # configurations.append({'domain_server': 148, 'domain_client': 58, 'auction_file': 'auction_psp.xml', 'request_file': 'aggregate_psp.xml'})
    # configurations.append({'domain_server': 149, 'domain_client': 59, 'auction_file': 'auction_subsidy.xml', 'request_file': 'aggregate_subsidy.xml'})
    # configurations.append({'domain_server': 150, 'domain_client': 60, 'auction_file': 'auction_two_auction_generalized.xml', 'request_file': 'aggregate_two_auction_generalized.xml'})

    for configuration in configurations:
        update_configuration_file('auction_agent.yaml', 'Main', 'Domain', str(configuration['domain_client']))
        update_configuration_file('auction_agent.yaml', 'Main', 'ResourceRequestFile', configuration['request_file'])

        update_configuration_file('auction_server.yaml', 'Main', 'Domain', str(configuration['domain_server']))
        update_configuration_file('auction_server.yaml', 'Main', 'AuctionFile', configuration['auction_file'])

        cmd_server = ['python', 'main_server.py']
        cmd_client = ['python', 'main_client.py']

        # start both programs - client and server
        proc_server = subprocess.Popen(cmd_server)
        proc_client = subprocess.Popen(cmd_client)

        # wait for their execution
        time.sleep(10000)

        # terminate both programs
        proc_client.send_signal(signal.SIGINT)
        proc_server.send_signal(signal.SIGINT)
