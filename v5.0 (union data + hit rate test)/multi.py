import multiprocessing as mp
import sys
import main_module
import os

def print_progress_bar(iteration, total, prefix='', length=50, fill='█'):
    percent = ("{:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}% Complete')
    sys.stdout.flush()

if __name__ == "__main__":
    
    number_of_days = 137

    bases = [
        169323466473.21405,  # 20km
        961554092.8640003, # 25km
        30606342.505,  # 30km
        2608613.8780000005,  # 35km
        411489.3269999999,  # 40km
        97845.52200000003, # 45km
        31008.934999999983,  # 50km
        12110.717000000004, # 55km
        5532.2990000000045,  # 60km
    ]

    radius = [
        20,
        25,
        30,
        35,
        40,
        45,
        50,
        55,
        60
    ]

    metrics = []

    operation_mode = 'parameter_search'

    growth_type = 'TG'

    count = 0

    print_progress_bar(count, 1, prefix='Progress:', length=50)

    for base in bases:
        args_list = [

            # SEARCH FOR THE BEST PARAMETERS

            [base, number_of_days, None, '/Trained_Data/all_together/arithmetic_mean_31_23', operation_mode, growth_type, 1, radius[bases.index(base)], 1.06, 1.04],
            [base, number_of_days, None, '/Trained_Data/all_together/geometric_mean_31_23', operation_mode, growth_type, 1, radius[bases.index(base)], 1.06, 1.04],
            [base, number_of_days, None, '/Trained_Data/all_together/harmonic_mean_31_23', operation_mode, growth_type, 1, radius[bases.index(base)], 1.06, 1.04],


            # CGNT and MG TESTING

            # [base, number_of_days, '/Trained_Data/all_together/arithmetic_mean_31_23', '/Test_Data/coletoressafra2021_31_23', operation_mode, growth_type, 1, radius[bases.index(base)], 1.06, 1.04],
            # [base, number_of_days, '/Trained_Data/all_together/arithmetic_mean_31_23', '/Test_Data/coletoressafra2122_31_23', operation_mode, growth_type, 1, radius[bases.index(base)], 1.06, 1.04],
            # [base, number_of_days, '/Trained_Data/all_together/arithmetic_mean_31_23', '/Test_Data/coletoressafra2223_31_23', operation_mode, growth_type, 1, radius[bases.index(base)], 1.06, 1.04],

            # [base, number_of_days, '/Trained_Data/all_together/geometric_mean_31_23', '/Test_Data/coletoressafra2021_31_23', operation_mode, growth_type, 1, radius[bases.index(base)], 1.06, 1.04],
            # [base, number_of_days, '/Trained_Data/all_together/geometric_mean_31_23', '/Test_Data/coletoressafra2122_31_23', operation_mode, growth_type, 1, radius[bases.index(base)], 1.06, 1.04],
            # [base, number_of_days, '/Trained_Data/all_together/geometric_mean_31_23', '/Test_Data/coletoressafra2223_31_23', operation_mode, growth_type, 1, radius[bases.index(base)], 1.06, 1.04],

            # [base, number_of_days, '/Trained_Data/all_together/harmonic_mean_31_23', '/Test_Data/coletoressafra2021_31_23', operation_mode, growth_type, 1, radius[bases.index(base)], 1.06, 1.04],
            # [base, number_of_days, '/Trained_Data/all_together/harmonic_mean_31_23', '/Test_Data/coletoressafra2122_31_23', operation_mode, growth_type, 1, radius[bases.index(base)], 1.06, 1.04],
            # [base, number_of_days, '/Trained_Data/all_together/harmonic_mean_31_23', '/Test_Data/coletoressafra2223_31_23', operation_mode, growth_type, 1, radius[bases.index(base)], 1.06, 1.04]

            # CGT TESTING

            # [base, number_of_days, '/Test_Data/coletoressafra2021_31_23', '/Test_Data/coletoressafra2122_31_23', operation_mode, growth_type, 4, radius[bases.index(base)]],
            # [base, number_of_days, '/Test_Data/coletoressafra2021_31_23', '/Test_Data/coletoressafra2223_31_23', operation_mode, growth_type, 4, radius[bases.index(base)]],

            # [base, number_of_days, '/Test_Data/coletoressafra2122_31_23', '/Test_Data/coletoressafra2021_31_23', operation_mode, growth_type, 4, radius[bases.index(base)]],
            # [base, number_of_days, '/Test_Data/coletoressafra2122_31_23', '/Test_Data/coletoressafra2223_31_23', operation_mode, growth_type, 4, radius[bases.index(base)]],

            # [base, number_of_days, '/Test_Data/coletoressafra2223_31_23', '/Test_Data/coletoressafra2021_31_23', operation_mode, growth_type, 4, radius[bases.index(base)]],
            # [base, number_of_days, '/Test_Data/coletoressafra2223_31_23', '/Test_Data/coletoressafra2122_31_23', operation_mode, growth_type, 4, radius[bases.index(base)]],
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

        count += num_processes
        total = len(bases) * num_processes

        print_progress_bar(count, total, prefix='Progress:', length=50)



    root_folder = None

    if 'Meu Drive' in os.getcwd():
        root_folder = 'Meu Drive'
    elif 'My Drive' in os.getcwd():
        root_folder = 'My Drive'

    if operation_mode == 'test':

        if not os.path.exists('G:/' + root_folder + f'/IC/Codes/Results/Growth_tests/{growth_type}.csv'):

            info = open('G:/' + root_folder + f'/IC/Codes/Results/Growth_tests/{growth_type}.csv', 'w', encoding='utf-8')

            if growth_type == 'CGT':
                info.write('growth_type,train_file,test_file,base,radius,number_of_days,true_positive,false_positive,days_error_mean_total,days_error_std_total,days_error_max_total,days_error_min_total,real_with_spores,real_without_spores,detected_with_spores,not_detected_with_spores,number_of_starting_points\n')
            elif growth_type == 'TG':
                info.write('growth_type,train_file,test_file,base,radius,number_of_days,true_positive,false_positive,days_error_mean_total,days_error_std_total,days_error_max_total,days_error_min_total,real_with_spores,real_without_spores,detected_with_spores,not_detected_with_spores,proportion_seg,proportion_larg\n')
            else:
                info.write('growth_type,train_file,test_file,base,radius,number_of_days,true_positive,false_positive,days_error_mean_total,days_error_std_total,days_error_max_total,days_error_min_total,real_with_spores,real_without_spores,detected_with_spores,not_detected_with_spores\n')

            info.close()
        
        info = open('G:/' + root_folder + f'/IC/Codes/Results/Growth_tests/{growth_type}.csv', 'a', encoding='utf-8')

        for _ in metrics:
            info.write(str(_).replace('[', '').replace(']', '').replace('\'', '') + '\n')
        
        info.close()

    elif operation_mode == 'parameter_search':

        if not os.path.exists(f'results_{growth_type}.csv'):

            f = open(f'results_{growth_type}.csv', 'w', encoding='utf-8')
            if growth_type == 'CGT':
                f.write(f"{'Method,Number of Days,Distance function,Days function,Base,Radius,Train file used,Test file used,TPP,TNP,FPP,FNP,number_of_starting_points'}\n")
            elif growth_type == 'TG':
                f.write(f"{'Method,Number of Days,Distance function,Days function,Base,Radius,Train file used,Test file used,TPP,TNP,FPP,FNP,rai,rpc,proportionSeg,proportionLarg'}\n")
            else:
                f.write(f"{'Method,Number of Days,Distance function,Days function,Base,Radius,Train file used,Test file used,TPP,TNP,FPP,FNP'}\n")
            f.close()
        
        f = open(f'results_{growth_type}.csv', 'a', encoding='utf-8')

        for i in range(len(metrics)):
            f.write(','.join(map(str, metrics[i]))+'\n')
        
        f.close()

