import multiprocessing as mp
import random
import main_module
import os

if __name__ == "__main__":
    
    number_of_days = 137
    # bases = random.sample(range(100, 12000), 20)

    # bases = [1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300]

    bases = [
        100000000,
        90000000,
        80000000,
        70000000,
        60000000,
        50000000,
        40000000,
        30000000,
        20000000,
        10000000,
        9000000,
        8000000,
        7000000,
        6000000,
        5000000,
        4000000,
        3000000,
        2000000,
        1000000,
        900000,
        800000,
        700000,
        600000,
        500000,
        400000,
        300000,
        200000,
        100000,
    ]

    metrics = []

    operation_mode = 'test'

    growth_type = 'MG'

    for base in bases:
        args_list = [

            # [base, number_of_days, None, 'coletoressafra2021_31_23', operation_mode, growth_type],
            # [base, number_of_days, None, 'coletoressafra2122_31_23', operation_mode, growth_type],
            # [base, number_of_days, None, 'coletoressafra2223_31_23', operation_mode, growth_type]

            [base, number_of_days, 'arithmetic_mean_31_23', 'coletoressafra2021_31_23', operation_mode, growth_type],
            [base, number_of_days, 'arithmetic_mean_31_23', 'coletoressafra2122_31_23', operation_mode, growth_type],
            [base, number_of_days, 'arithmetic_mean_31_23', 'coletoressafra2223_31_23', operation_mode, growth_type],

            [base, number_of_days, 'geometric_mean_31_23', 'coletoressafra2021_31_23', operation_mode, growth_type],
            [base, number_of_days, 'geometric_mean_31_23', 'coletoressafra2122_31_23', operation_mode, growth_type],
            [base, number_of_days, 'geometric_mean_31_23', 'coletoressafra2223_31_23', operation_mode, growth_type],

            [base, number_of_days, 'harmonic_mean_31_23', 'coletoressafra2021_31_23', operation_mode, growth_type],
            [base, number_of_days, 'harmonic_mean_31_23', 'coletoressafra2122_31_23', operation_mode, growth_type],
            [base, number_of_days, 'harmonic_mean_31_23', 'coletoressafra2223_31_23', operation_mode, growth_type]

            # [base, number_of_days, '2021-2122', 'coletoressafra2223_31_23', operation_mode, growth_type],
            # [base, number_of_days, '2021-2223', 'coletoressafra2122_31_23', operation_mode, growth_type],
            # [base, number_of_days, '2122-2223', 'coletoressafra2021_31_23', operation_mode, growth_type],
        ]

        if len(args_list) == 0:

            print('No arguments to run!')
            exit()

        num_processes = len(args_list)
        pool = mp.Pool(processes=num_processes)

        # Use the main function from the imported module
        temp_metrics = pool.starmap(main_module.main, args_list)

        metrics.extend(temp_metrics)

        pool.close()
        pool.join()

    root_folder = None

    if 'Meu Drive' in os.getcwd():
        root_folder = 'Meu Drive'
    elif 'My Drive' in os.getcwd():
        root_folder = 'My Drive'

    if operation_mode == 'test':


        info = open('G:/' + root_folder + f'/IC/Codes/Results/Growth_tests/{growth_type}.csv', 'w', encoding='utf-8')

        info.write('train_file,test_file,base,number_of_days,true_positive,false_positive,days_error_mean_north,days_error_mean_east,days_error_mean_south,days_error_mean_west,days_error_max_north,days_error_max_east,days_error_max_south,days_error_max_west,days_error_min_north,days_error_min_east,days_error_min_south,days_error_min_west,days_error_std_north,days_error_std_east,days_error_std_south,days_error_std_west,days_error_mean_total,days_error_max_total,days_error_min_total,days_error_std_total,real_with_spores,real_without_spores,detected_with_spores,not_detected_with_spores\n')

        for _ in metrics:
            info.write(str(_).replace('[', '').replace(']', '').replace('\'', '') + '\n')
        
        info.close()

    elif operation_mode == 'parameter_search':

        if not os.path.exists(f'results_{growth_type}.csv'):
            f = open(f'results_{growth_type}.csv', 'w', encoding='utf-8')
            f.write(f"{'Method,Number of Days,Distance function,Days function,Base,Train file used,Test file used,TPP,TNP,FPP,FNP'}\n")
            f.close()
        
        f = open(f'results_{growth_type}.csv', 'a', encoding='utf-8')

        for i in range(len(metrics)):
            f.write(','.join(map(str, metrics[i]))+'\n')
        
        f.close()

