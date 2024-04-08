import numpy as np
from EMQST_lib import support_functions as sf



def measurement(n_shots, povm, rho, bool_exp_measurements = False, exp_dictionary = None, state_angle_representation = None, custom_measurement_function = None, return_frequencies = False):
    """
    Measurment settings and selects either experimental or simulated measurements. 
    For experimental measurements some settings are converted to angle arrays. 
    """

    if bool_exp_measurements:
        if custom_measurement_function is None:
            if state_angle_representation is None:
                print("Experimental measurement: No angle representation has been given! Returning None.")
                return np.array([None]*n_shots) 
            outcome_index = exp_dictionary["standard_measurement_function"](n_shots,povm.get_angles(),state_angle_representation,exp_dictionary)
        else:
            outcome_index = custom_measurement_function(n_shots,povm.get_angles(),exp_dictionary)
    else:
        outcome_index = simulated_measurement(n_shots,povm,rho,return_frequencies)
        
    return outcome_index


def simulated_measurement(n_shots,povm,rho, return_frequencies = False):
    """
    Takes in number of shots required from a single POVM on a single quantum states.
    Returns and outcome_index vector where the index corresponds the the POVM that occured.
    """

    # Find probabilites for different outcomes
    histogram = povm.get_histogram(rho)

    # Create cumulative sum
    cumulative_sum = np.cumsum(histogram)

    # Sample outcomes 
    r = np.random.random(n_shots)

    # Return index list of outcomes 
    outcome_list = np.searchsorted(cumulative_sum, r)
    if return_frequencies:
            
        min_unique_outcomes = len(histogram)
        frequencies = outcomes_to_frequencies(outcome_list,min_unique_outcomes)
        return frequencies
    else:    
        return outcome_list

def outcomes_to_frequencies(outcomes,min_lenght):
    # Count the occurrences of each outcome
    unique_outcomes, frequencies = np.unique(outcomes, return_counts=True)


    if len(unique_outcomes) < min_lenght:
        # Pad frequencies where unique_elements_to_contain does not appear in unique_found
        missing_outcomes = np.setdiff1d(np.arange(min_lenght), unique_outcomes)
        # Insert where we have the missing outcome in the list (loop to keep )
        for outcome in missing_outcomes:
            frequencies = np.insert(frequencies, outcome, 0)
    return frequencies

def measure_separable_state(n_shots, povm_array, rho_array):
    """
    Takes in a list of single qubit states, a list of single qubit POVMs, and the number of shots.
    Returns a list of outcomes for each qubit. Each measurement is sampled independently for each qubit.
    This function is designed to be used for large system sizes.

    Parameters:
    - n_shots (int): The number of shots for each measurement.
    - povm_list (ndarray): A numpy array of single qubit POVMs.
    - rho_list (ndarray): A numpy array of single qubit states.

    Returns:
    - outcomes (ndarray): A numpy array of shape (n_shots, n_qubits) containing the outcomes for each qubit.
    """
    
    n_qubits = len(rho_array)
    outcomes_temp = np.array([simulated_measurement(n_shots, povm_array[i], rho_array[i]) for i in range(n_qubits)])
    # Change axis such that order matches what is expected from experiments.
    outcomes = np.moveaxis(outcomes_temp, 0, -1)
    return outcomes


