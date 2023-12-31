#  file: combine_copy_nums.py
#  author: Jingyi Wang and Xuecong Fu
#  this file is originally from tusv codes by Jingyi Wang to 
#  combine list of triplets into triplet according to list of 
#  usages and modified by Xuecong Fu to add allelic copy numbers

#############
# Functions #
#############

# type(triplets) = list, each triplet has 3 lists (bgns, ends, cps)
# type(usages) = list
#  input: triplets (3D list) [num_chromosomes by 3 by num_segments]
#                            triplets[k, 0, s] is beginning position for segment s on chromosome k
#                            triplets[k, 1, s] is ending    position for segment s on chromosome k
#                            triplets[k, 2, s] is copy number        for segment s on chromosome k
#         usages (list of float) [num_chromosomes] long. usages[k] is weight (percent) of chromosome k
# output: bgns (list of int) [num_unioned_segments] bgns[s] is beginning position of segment s
#         ends (list of int) [num_unioned_segments] ends[s] is ending    position of segment s
#         cps  (list of int) [num_unioned_segments] cps[s]  is fractional copy number of segment s
def combine_copy_nums_quartet(quartets, usages):
	posList, pos_dir_dict = get_pos_info_dict_quartet(quartets) ### xf: create position dictionary

	combined_segment_pos_list = get_combined_segment_pos(posList, pos_dir_dict) # list of (bgnPos,endPos) ### xf: combining segments settings from different nodes

	bgn2idx, end2idx = get_indices_dict(combined_segment_pos_list) # key: bgn or end position, val: idx of segment in combined chrom

	res_bgns, res_ends = list(), list()
	for (bgnPos,endPos) in combined_segment_pos_list:
		res_bgns.append(bgnPos)
		res_ends.append(endPos)

	res_cps = [[0] * len(res_bgns)] * 2
	for i in range(len(quartets)):
		[bgns, ends, cps1, cps2] = quartets[i]
		cps = [cps1, cps2]
		for j in range(len(bgns)):
			idx_list = get_indices_for_segment(bgn2idx, end2idx, bgns[j], ends[j])
			for k in idx_list: ### xf: find the corresponding indices for combined segments for ith triplet
				res_cps[0][k] += float("{0:.2f}".format(cps[0][j] * usages[i]))
				res_cps[1][k] += float("{0:.2f}".format(cps[1][j] * usages[i]))

	return [res_bgns, res_ends, res_cps[0], res_cps[1]] ### xf: allelic specific CNs
	
def combine_copy_nums_allelic(triplets, usages):
	posList, pos_dir_dict = get_pos_info_dict(triplets) ### xf: create position dictionary

	combined_segment_pos_list = get_combined_segment_pos(posList, pos_dir_dict) # list of (bgnPos,endPos)

	bgn2idx, end2idx = get_indices_dict(combined_segment_pos_list) # key: bgn or end position, val: idx of segment in combined chrom
	res_bgns, res_ends = list(), list()
	for (bgnPos,endPos) in combined_segment_pos_list:
		res_bgns.append(bgnPos)
		res_ends.append(endPos)

	res_cps = [[0] * len(res_bgns)] + [[0] * len(res_bgns)]
	for i in range(len(triplets)):
		[bgns, ends, cps] = triplets[i]
		for j in range(len(bgns)):
			idx_list = get_indices_for_segment(bgn2idx, end2idx, bgns[j], ends[j])
			for k in idx_list:
				res_cps[i][k] += float("{0:.2f}".format(cps[j] * usages[i]))
	return [res_bgns, res_ends, res_cps[0], res_cps[1]] ### xf: allelic specific CNs

def get_pos_info_dict(triplets):
	posSet = set() # combine bgn and end positions
	pos_dir_dict = dict() # key: pos, val: ['bgn'] or ['end'] or ['end','bgn']
	for i in range(len(triplets)):
		[bgns, ends, cps] = triplets[i]
		for j in range(len(bgns)):
			posSet.add(bgns[j])
			posSet.add(ends[j])
			if bgns[j] not in pos_dir_dict:
				pos_dir_dict[bgns[j]] = ['bgn']
			else:
				if 'bgn' not in pos_dir_dict[bgns[j]]:
					pos_dir_dict[bgns[j]] += ['bgn']
			if ends[j] not in pos_dir_dict:
				pos_dir_dict[ends[j]] = ['end']
			else:
				if 'end' not in pos_dir_dict[ends[j]]:
					pos_dir_dict[ends[j]] += ['end']
	posList = sorted(list(posSet))
	return posList, pos_dir_dict

def get_pos_info_dict_quartet(quartets):
	posSet = set() # combine bgn and end positions
	pos_dir_dict = dict() # key: pos, val: ['bgn'] or ['end'] or ['end','bgn']
	for i in range(len(quartets)):
		[bgns, ends, cps1, cps2] = quartets[i]
		for j in range(len(bgns)):
			posSet.add(bgns[j])
			posSet.add(ends[j])
			if bgns[j] not in pos_dir_dict:
				pos_dir_dict[bgns[j]] = ['bgn']
			else:
				if 'bgn' not in pos_dir_dict[bgns[j]]:
					pos_dir_dict[bgns[j]] += ['bgn']
			if ends[j] not in pos_dir_dict:
				pos_dir_dict[ends[j]] = ['end']
			else:
				if 'end' not in pos_dir_dict[ends[j]]:
					pos_dir_dict[ends[j]] += ['end']
	posList = sorted(list(posSet))
	return posList, pos_dir_dict

# return (bgn, end) position for combined segment, eg. [(bgn1, end1), (bgn2, end2), ...]
def get_combined_segment_pos(posList, pos_dir_dict):
	result = list()
	tempBgn = posList[0]
	i = 0

	while i < len(posList) - 1:
		# end at this position
		if 'end' in pos_dir_dict[posList[i]]:
			tempEnd = posList[i]
			result.append((tempBgn, tempEnd))

			if 'bgn' in pos_dir_dict[posList[i + 1]]:
				tempBgn = posList[i + 1]
			else:
				tempBgn = posList[i] + 1
			i += 1
		# not end at this position
		else:
			if 'bgn' in pos_dir_dict[posList[i + 1]] and 'end' not in pos_dir_dict[posList[i + 1]]:
				tempEnd = posList[i + 1] - 1
				result.append((tempBgn, tempEnd))
				tempBgn = posList[i + 1]
				i += 1
			elif 'end' in pos_dir_dict[posList[i + 1]] and 'bgn' not in pos_dir_dict[posList[i + 1]]:
				tempEnd = posList[i + 1]
				result.append((tempBgn, tempEnd))
				if tempEnd == posList[-1]:
					break
				else:
					tempBgn = posList[i + 2]
				i += 2
			else:
				tempEnd = posList[i + 1] - 1
				result += [(tempBgn, tempEnd), (posList[i + 1], posList[i + 1])]
				tempBgn = posList[i + 1] + 1
				i += 1

	# last element in posList
	if tempBgn == posList[-1]:
		result.append((tempBgn, tempBgn))
	return result


def get_indices_dict(combined_segment_pos_list):
	bgn2idx = dict()
	end2idx = dict()
	idx = 0
	for (s,e) in combined_segment_pos_list:
		bgn2idx[s] = idx
		end2idx[e] = idx
		idx += 1
	return bgn2idx, end2idx


# given start and end position, output list of segment indices (continuous)
def get_indices_for_segment(bgn2idx, end2idx, s, e):
	result = list()
	firstIdx = bgn2idx[s]
	lastIdx = end2idx[e]
	for i in range(firstIdx, lastIdx + 1):
		result.append(i)
	return result
