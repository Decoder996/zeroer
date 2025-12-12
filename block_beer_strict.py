# Alternative blocking strategies for beer dataset
# This file contains experimental blocking functions for testing

import py_entitymatching as em

def block_beer_strict_4(A, B):
    """Very strict blocking with overlap_size=4"""
    ob = em.OverlapBlocker()
    attributes = ['Beer_Name', 'Brew_Factory_Name', 'Style', 'ABV']
    l_output_attrs = [col for col in attributes if col in A.columns]
    r_output_attrs = [col for col in attributes if col in B.columns]
    C = ob.block_tables(A, B, 'Beer_Name', 'Beer_Name', word_level=True, overlap_size=4,
                        l_output_attrs=l_output_attrs, r_output_attrs=r_output_attrs,
                        show_progress=True, allow_missing=True)
    return C

def block_beer_two_stage(A, B):
    """Two-stage blocking: Beer_Name then Brew_Factory_Name"""
    ob = em.OverlapBlocker()
    attributes = ['Beer_Name', 'Brew_Factory_Name', 'Style', 'ABV']
    l_output_attrs = [col for col in attributes if col in A.columns]
    r_output_attrs = [col for col in attributes if col in B.columns]
    
    # Stage 1: Block by Beer_Name
    C1 = ob.block_tables(A, B, 'Beer_Name', 'Beer_Name', word_level=True, overlap_size=2,
                         l_output_attrs=l_output_attrs, r_output_attrs=r_output_attrs,
                         show_progress=True, allow_missing=True)
    
    # Stage 2: Further filter by Brew_Factory_Name
    if 'Brew_Factory_Name' in A.columns and 'Brew_Factory_Name' in B.columns:
        C2 = ob.block_candset(C1, 'ltable_Brew_Factory_Name', 'rtable_Brew_Factory_Name', 
                              word_level=True, overlap_size=2, show_progress=True)
        return C2
    return C1

def block_beer_combined(A, B):
    """Combined blocking: Beer_Name overlap_size=3 + Brew_Factory_Name overlap_size=2"""
    ob = em.OverlapBlocker()
    attributes = ['Beer_Name', 'Brew_Factory_Name', 'Style', 'ABV']
    l_output_attrs = [col for col in attributes if col in A.columns]
    r_output_attrs = [col for col in attributes if col in B.columns]
    
    # Stage 1: Block by Beer_Name with overlap_size=3
    C1 = ob.block_tables(A, B, 'Beer_Name', 'Beer_Name', word_level=True, overlap_size=3,
                         l_output_attrs=l_output_attrs, r_output_attrs=r_output_attrs,
                         show_progress=True, allow_missing=True)
    
    # Stage 2: Further filter by Brew_Factory_Name with overlap_size=2
    if 'Brew_Factory_Name' in A.columns and 'Brew_Factory_Name' in B.columns:
        C2 = ob.block_candset(C1, 'ltable_Brew_Factory_Name', 'rtable_Brew_Factory_Name', 
                              word_level=True, overlap_size=2, show_progress=True)
        return C2
    return C1

