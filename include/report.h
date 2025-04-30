/**
 * @file report.h
 * @brief Header file for report generation functions
 *
 * This file contains declarations for functions related to generating
 * various reports for the property management system.
 */

#ifndef REPORT_H
#define REPORT_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include "property.h"
#include "residential.h"
#include "commercial.h"
#include "land.h"
#include "utils.h"

/**
 * @brief Generate a report of all properties by type
 * 
 * @param output_file Path to the output file
 * @return int 0 on success, error code otherwise
 */
int report_generate_property_type_summary(const char* output_file);

/**
 * @brief Generate a report of properties by district
 * 
 * @param output_file Path to the output file
 * @param deal_type Deal type (sale or rent)
 * @return int 0 on success, error code otherwise
 */
int report_generate_district_summary(const char* output_file, const char* deal_type);

/**
 * @brief Generate a report of property value by type
 * 
 * @param output_file Path to the output file
 * @return int 0 on success, error code otherwise
 */
int report_generate_property_value_summary(const char* output_file);

/**
 * @brief Generate a report of properties by price range
 * 
 * @param output_file Path to the output file
 * @param min_price Minimum price
 * @param max_price Maximum price
 * @param num_ranges Number of price ranges
 * @param deal_type Deal type (sale or rent)
 * @return int 0 on success, error code otherwise
 */
int report_generate_price_range_summary(const char* output_file, int min_price, 
                                       int max_price, int num_ranges, const char* deal_type);

/**
 * @brief Generate a CSV export of properties
 * 
 * @param output_file Path to the output file
 * @param property_type Property type (residential, commercial, land)
 * @param deal_type Deal type (sale or rent)
 * @return int 0 on success, error code otherwise
 */
int report_export_properties_csv(const char* output_file, const char* property_type, const char* deal_type);

#endif /* REPORT_H */ 