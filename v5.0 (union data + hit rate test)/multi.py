import multiprocessing as mp
import random
import main_module
import os

if __name__ == "__main__":
    
    number_of_days = 137
    bases = random.sample(range(100, 1000000), 10)

    metrics = []

    Looking_for_parameter = True

    Testing = False

    Circular_growth_no_touch = False

    Circular_growth_touch = True

    Topology_growth = False

    for base in bases:
        args_list = [
         [base, number_of_days, None, 'coletoressafra2021_31_23', Looking_for_parameter, Testing, Circular_growth_no_touch, Circular_growth_touch, Topology_growth],
         [base, number_of_days, None, 'coletoressafra2122_31_23', Looking_for_parameter, Testing, Circular_growth_no_touch, Circular_growth_touch, Topology_growth],
         [base, number_of_days, None, 'coletoressafra2223_31_23', Looking_for_parameter, Testing, Circular_growth_no_touch, Circular_growth_touch, Topology_growth]]

        num_processes = len(args_list)
        pool = mp.Pool(processes=num_processes)

        # Use the main function from the imported module
        temp_metrics = pool.starmap(main_module.main, args_list)

        metrics.extend(temp_metrics)

        pool.close()
        pool.join()

    if Testing:

        root_folder = None

        if 'Meu Drive' in os.getcwd():
            root_folder = 'Meu Drive'
        elif 'My Drive' in os.getcwd():
            root_folder = 'My Drive'

        info = open('G:/' + root_folder + '/IC/Codes/Results/Growth_tests/all_means.csv', 'w', encoding='utf-8')

        info.write('train_file, test_file,base,number_of_days,true_positive,false_positive,days_error_mean_north,days_error_mean_east,days_error_mean_south,days_error_mean_west,days_error_max_north,days_error_max_east,days_error_max_south,days_error_max_west,days_error_min_north,days_error_min_east,days_error_min_south,days_error_min_west,days_error_std_north,days_error_std_east,days_error_std_south,days_error_std_west,days_error_mean_total,days_error_max_total,days_error_min_total,days_error_std_total,real_with_spores,real_without_spores,detected_with_spores,not_detected_with_spores\n')

        for _ in metrics:
            info.write(str(_).replace('[', '').replace(']', '').replace('\'', '') + '\n')
        
        info.close()