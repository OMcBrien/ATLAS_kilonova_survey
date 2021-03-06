import numpy as np
import matplotlib.pyplot as plt
import random

def getShellWeights(lower_redshift_limit, upper_redshift_limit, num_redshift_bins):

	num_shells = num_redshift_bins - 1
	redshift_distribution = np.linspace(lower_redshift_limit, upper_redshift_limit, num_redshift_bins)
	c = 2.99792458e5 # Speed of light in km/s
	H_0 = 70.0		 # Hubble constant (km/s/Mpc)
	
	upper_redshift_bounds = redshift_distribution[1:]
	lower_redshift_bounds = redshift_distribution[:-1]
	
	upper_volume_distribution = (4./3.) * np.pi * (c * upper_redshift_bounds / H_0)**3	
	lower_volume_distribution = (4./3.) * np.pi * (c * lower_redshift_bounds / H_0)**3	
	shell_volume_distribution = (upper_volume_distribution - lower_volume_distribution)
	
# 	shell_weights = shell_volume_distribution / np.nanmax(upper_volume_distribution)
	shell_weights = shell_volume_distribution / np.sum(shell_volume_distribution)
	
# 	for i in range(0, len(upper_redshift_bounds)):
# 		print('z = %f to %f has weight %f' %(lower_redshift_bounds[i], upper_redshift_bounds[i], shell_weights[i]))
	
# 	print(np.sum(shell_weights))
	
	return shell_weights, redshift_distribution
	
# ========================================================================================

def getBandWeights(lower_declination_limit, upper_declination_limit, declination_band_width):

	declination_distribution = np.arange(lower_declination_limit, upper_declination_limit + 1, declination_band_width)
	
	band_midpoints = np.empty(len(declination_distribution) - 1)
	
	for i in range(1, len(declination_distribution)):
	
		band_midpoints[i-1] = declination_distribution[i-1] + (declination_distribution[i] - declination_distribution[i-1]) / 2.0
	
	band_weights = np.cos(band_midpoints * np.pi / 180.)
	
# 	for i in range(1, len(declination_distribution)):
# 		print('Dec = %f to %f has midpoint %f and weight %f' %(declination_distribution[i-1], declination_distribution[i], band_midpoints[i-1], band_weights[i-1]))
		
	return band_weights, declination_distribution
	
# ========================================================================================

def getRedshiftBounds(shell_weights, redshift_distribution):

    weights_sum = shell_weights.sum()
    # standardization:
    np.multiply(shell_weights, 1. / weights_sum, shell_weights)
    shell_weights_cumulative_sum = shell_weights.cumsum()
    
    x = random.random()
    
    for i in range(len(shell_weights_cumulative_sum)):
        
        if x < shell_weights_cumulative_sum[i]:
            
            return redshift_distribution[i], redshift_distribution[i+1]

# ========================================================================================

def getDeclinationBounds(band_weights, declination_distribution):

    weights_sum = band_weights.sum()
    # standardization:
    np.multiply(band_weights, 1. / weights_sum, band_weights)
    band_weights_cumulative_sum = band_weights.cumsum()
    
    x = random.random()
    
    for i in range(len(band_weights_cumulative_sum)):
        
        if x < band_weights_cumulative_sum[i]:
            
            return declination_distribution[i], declination_distribution[i+1]

# ========================================================================================

def filterQualityControlDataFrameByExplosionEpoch(full_QC_df, QC_columns, transient, lower_fit_time_limit, upper_fit_time_limit):

	lower_expl_epoch_bound = transient.expl_epoch + lower_fit_time_limit
	upper_expl_epoch_bound = transient.expl_epoch + upper_fit_time_limit
	
	partial_QC_df = full_QC_df.query('%s >= %f & %s <= %f' %(QC_columns['qc_time'], lower_expl_epoch_bound, QC_columns['qc_time'], upper_expl_epoch_bound))

	return partial_QC_df
	
# ========================================================================================
	
def filterQualityControlDataFrameByCoords(partial_QC_df, QC_columns, transient, chipwidth, plot_mode = False):

	chip_halfwidth = chipwidth / 2. # degrees
	chipwidth = chip_halfwidth * 2.
	
	max_allowed_ra = 360.
	min_allowed_ra = 0.

	upper_transient_ra_bound = transient.ra + (chipwidth * np.cos(transient.dec*np.pi/180.)) / 2.
	lower_transient_ra_bound = transient.ra - (chipwidth * np.cos(transient.dec*np.pi/180.)) / 2.
	upper_transient_ra_bound_unc = transient.ra + (chipwidth) / 2.
	lower_transient_ra_bound_unc = transient.ra - (chipwidth) / 2.
	upper_transient_dec_bound = transient.dec + chip_halfwidth
	lower_transient_dec_bound = transient.dec - chip_halfwidth
	
# 	if plot_mode:
# 
# 		SMALL_SIZE = 15
# 		MEDIUM_SIZE = 20
# 		BIGGER_SIZE = 25
# 
# 		plt.rc('font', size=SMALL_SIZE)          	# controls default text sizes
# 		plt.rc('axes', titlesize=BIGGER_SIZE)     	# fontsize of the axes title
# 		plt.rc('axes', labelsize=MEDIUM_SIZE)    	# fontsize of the x and y labels
# 		plt.rc('xtick', labelsize=SMALL_SIZE)    	# fontsize of the tick labels
# 		plt.rc('ytick', labelsize=SMALL_SIZE)    	# fontsize of the tick labels
# 		plt.rc('legend', fontsize=MEDIUM_SIZE)    	# legend fontsize
# 		plt.rc('figure', titlesize=BIGGER_SIZE)  	# fontsize of the figure title
# 
# 		plt.rcParams["font.family"] = "serif"
# 		plt.rcParams['mathtext.fontset'] = 'dejavuserif'
# 	
# 		fig = plt.figure(figsize = (12, 10))
# 		ax = fig.add_subplot(111)
# 	
# 		ra_array = np.array([lower_transient_ra_bound, upper_transient_ra_bound, upper_transient_ra_bound, lower_transient_ra_bound, lower_transient_ra_bound])
# 		ra_array_unc = np.array([lower_transient_ra_bound_unc, upper_transient_ra_bound_unc, upper_transient_ra_bound_unc, lower_transient_ra_bound_unc, lower_transient_ra_bound_unc])
# 		dec_array = np.array([lower_transient_dec_bound, lower_transient_dec_bound, upper_transient_dec_bound, upper_transient_dec_bound, lower_transient_dec_bound])
# 	
# 		ax.plot(transient.ra, transient.dec, ls = 'None', marker = 'o', mfc = 'red', mec = 'black', ms = 10)
# 		ax.plot(ra_array_unc, dec_array, ls = '--', marker = 'None', color = 'red', label = 'normal')
# 		ax.plot(ra_array, dec_array, ls = '--', marker = 'None', color = 'blue', label = 'corrected')
# 	
# 		plt.xlabel('RA, degrees')
# 		plt.ylabel('Dec, degrees')
# 		plt.legend(loc = 'upper center', frameon = False, ncol = 2, bbox_to_anchor = (0.50, 1.15))
# 		plt.show(fig)
	
	# Filter RA first as it wraps (360 --> 0 degrees)
	if upper_transient_ra_bound > max_allowed_ra:
	
		partial_QC_df = partial_QC_df.query('%s >= %f | %s <= %f' %(QC_columns['qc_ra'], lower_transient_ra_bound, QC_columns['qc_ra'], (upper_transient_ra_bound - max_allowed_ra)) )
	
	elif lower_transient_ra_bound < min_allowed_ra:
	
		partial_QC_df = partial_QC_df.query('%s >= %f | %s <= %f' %(QC_columns['qc_ra'], (lower_transient_ra_bound + max_allowed_ra), QC_columns['qc_ra'], (upper_transient_ra_bound - max_allowed_ra)) )
	
	else:

		partial_QC_df = partial_QC_df.query('%s >= %f & %s <= %f' %(QC_columns['qc_ra'], lower_transient_ra_bound, QC_columns['qc_ra'], upper_transient_ra_bound) )
	
	# Now filter by DEC
	partial_QC_df = partial_QC_df.query('%s >= %f & %s <= %f' %(QC_columns['qc_dec'], lower_transient_dec_bound, QC_columns['qc_dec'], upper_transient_dec_bound) )
	
# 	partial_QC_df = partial_QC_df.query('RA >= %f & RA <= %f & DEC >= %f & DEC <= %f' %(lower_transient_ra_bound, upper_transient_ra_bound, lower_transient_dec_bound, upper_transient_dec_bound))

	return partial_QC_df

# ========================================================================================

def fitTransientLightcurve(transient_df, lower_fit_time_limit, upper_fit_time_limit, polynomial_degree, save_results = False, results_directory = 'test'):

	transient_df_cyan = transient_df.query('c.notnull()', engine = 'python')
	transient_df_orange = transient_df.query('o.notnull()', engine = 'python')
	
# 	print(transient_df_cyan)
# 	print(transient_df_orange)

	phase_c = transient_df_cyan['phase']
	c_lc = transient_df_cyan['c']
	c_err = transient_df_cyan['cerr']
	phase_o = transient_df_orange['phase']
	o_lc = transient_df_orange['o']
	o_err = transient_df_orange['oerr']
	
	p_c = np.poly1d(np.polyfit(phase_c, c_lc, polynomial_degree))
	p_o = np.poly1d(np.polyfit(phase_o, o_lc, polynomial_degree))

	if save_results:

		SMALL_SIZE = 15
		MEDIUM_SIZE = 20
		BIGGER_SIZE = 25

		plt.figure(figsize = (12,10))

		plt.rc('font', size=SMALL_SIZE)          	# controls default text sizes
		plt.rc('axes', titlesize=BIGGER_SIZE)     	# fontsize of the axes title
		plt.rc('axes', labelsize=MEDIUM_SIZE)    	# fontsize of the x and y labels
		plt.rc('xtick', labelsize=SMALL_SIZE)    	# fontsize of the tick labels
		plt.rc('ytick', labelsize=SMALL_SIZE)    	# fontsize of the tick labels
		plt.rc('legend', fontsize=MEDIUM_SIZE)    	# legend fontsize
		plt.rc('figure', titlesize=BIGGER_SIZE)  	# fontsize of the figure title

		plt.rcParams["font.family"] = "serif"
		plt.rcParams['mathtext.fontset'] = 'dejavuserif'
		
		plt.errorbar(phase_c, c_lc, c_err, ls = 'None', marker = 'o', ms = 8, mfc = 'cyan', mec = 'black', ecolor = 'black', capsize = 5)
		plt.errorbar(phase_o, o_lc, o_err, ls = 'None', marker = 'o', ms = 8, mfc = 'orange', mec = 'black', ecolor = 'black', capsize = 5)
	
		time_array = np.arange(lower_fit_time_limit, upper_fit_time_limit, 0.1)
	
		plt.plot(time_array, p_c(time_array), ls = '-', color = 'green', marker = '|', mfc = 'green', mec = 'green', ms = 10)
		plt.plot(time_array, p_o(time_array), ls = '-', color = 'red', marker = '|', mfc = 'red', mec = 'red', ms = 10)

		plt.title('Polynomial fit, $k = %d$' %polynomial_degree)
		plt.xlabel('Phase, days')
		plt.ylabel('Magnitude')
		plt.gca().invert_yaxis()
		plt.tight_layout()
		
		plt.savefig('results/' + results_directory + '/polynomial_k_%d.pdf' %polynomial_degree)
		plt.close()
	
	return p_c, p_o












